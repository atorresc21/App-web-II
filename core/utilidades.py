"""Reglas de negocio y funciones de apoyo de Axon Budget."""
from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from .models import Gasto, Ingreso

# Regla básica de planificación: se sugiere ahorrar el 20 % de los ingresos
# del mes, siempre que alcance después de pagar los gastos.
PORCENTAJE_AHORRO = Decimal("0.20")

NOMBRES_MES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def cop(valor):
    """Da formato de pesos colombianos: 1200000 -> $ 1.200.000"""
    valor = int(valor or 0)
    signo = "-" if valor < 0 else ""
    return signo + "$ {:,}".format(abs(valor)).replace(",", ".")


def _suma_del_mes(modelo, usuario, hoy):
    total = modelo.objects.filter(
        usuario=usuario, fecha__year=hoy.year, fecha__month=hoy.month
    ).aggregate(total=Sum("monto"))["total"]
    return int(total or 0)


def calcular_plan(usuario, hoy=None):
    """Reparte los ingresos del mes entre gastos, ahorro y dinero disponible."""
    hoy = hoy or timezone.localdate()
    ingresos = _suma_del_mes(Ingreso, usuario, hoy)
    gastos = _suma_del_mes(Gasto, usuario, hoy)

    sobrante = max(ingresos - gastos, 0)
    ahorro = min(int(ingresos * PORCENTAJE_AHORRO), sobrante)
    disponible = ingresos - gastos - ahorro

    base = max(ingresos, gastos)
    pct_gastos = round(gastos * 100 / base) if base else 0
    pct_ahorro = round(ahorro * 100 / base) if base else 0
    pct_disponible = max(0, 100 - pct_gastos - pct_ahorro) if base else 0

    return {
        "ingresos": ingresos,
        "gastos": gastos,
        "ahorro": ahorro,
        "disponible": disponible,
        "pct_gastos": pct_gastos,
        "pct_ahorro": pct_ahorro,
        "pct_disponible": pct_disponible,
        "sin_movimientos": ingresos == 0 and gastos == 0,
        "supera": gastos > ingresos,
    }


def inicio_periodo(periodo, hoy):
    """Fecha desde la que se filtra el historial (semana, quincena o mes)."""
    if periodo == "semana":
        return hoy - timedelta(days=hoy.weekday())
    if periodo == "quincena":
        return hoy.replace(day=1 if hoy.day <= 15 else 16)
    if periodo == "mes":
        return hoy.replace(day=1)
    return None


def movimientos(usuario, desde=None):
    """Une ingresos y gastos en una sola lista, del más reciente al más antiguo."""
    ingresos = Ingreso.objects.filter(usuario=usuario)
    gastos = Gasto.objects.filter(usuario=usuario)
    if desde:
        ingresos = ingresos.filter(fecha__gte=desde)
        gastos = gastos.filter(fecha__gte=desde)

    lista = []
    for i in ingresos:
        lista.append({
            "fecha": i.fecha, "tipo": "Ingreso", "descripcion": i.descripcion,
            "detalle": i.get_periodicidad_display(), "monto": int(i.monto),
        })
    for g in gastos:
        lista.append({
            "fecha": g.fecha, "tipo": "Gasto", "descripcion": g.descripcion,
            "detalle": g.get_categoria_display(), "monto": int(g.monto),
        })
    lista.sort(key=lambda m: m["fecha"], reverse=True)
    return lista
