from django.shortcuts import render


def cop(valor):
    """Da formato de pesos colombianos: 1200000 -> $ 1.200.000"""
    return "$ {:,.0f}".format(valor).replace(",", ".")


# Datos de ejemplo: en las próximas clases se reemplazan por la base de datos.
INGRESOS = [
    {"fecha": "28/10/2026", "descripcion": "Pago quincenal", "periodicidad": "Quincenal", "monto": cop(900000)},
    {"fecha": "20/10/2026", "descripcion": "Trabajo extra", "periodicidad": "Variable", "monto": cop(150000)},
    {"fecha": "13/10/2026", "descripcion": "Pago quincenal", "periodicidad": "Quincenal", "monto": cop(900000)},
]

GASTOS = [
    {"fecha": "27/10/2026", "descripcion": "Arriendo", "categoria": "Vivienda", "tipo": "Fijo", "monto": cop(500000)},
    {"fecha": "25/10/2026", "descripcion": "Transporte", "categoria": "Transporte", "tipo": "Variable", "monto": cop(80000)},
    {"fecha": "24/10/2026", "descripcion": "Mercado", "categoria": "Alimentación", "tipo": "Variable", "monto": cop(220000)},
    {"fecha": "20/10/2026", "descripcion": "Internet", "categoria": "Servicios", "tipo": "Fijo", "monto": cop(90000)},
]

METAS = [
    {"nombre": "Fondo de emergencia", "principal": True, "avance": 45, "ahorrado": cop(450000), "objetivo": cop(1000000)},
    {"nombre": "Viaje a San Andrés", "principal": False, "avance": 20, "ahorrado": cop(200000), "objetivo": cop(1000000)},
    {"nombre": "Computador nuevo", "principal": False, "avance": 10, "ahorrado": cop(150000), "objetivo": cop(1500000)},
]

PAGOS = [
    {"nombre": "Arriendo", "fecha": "01/11/2026", "faltan": "3 días", "monto": cop(500000)},
    {"nombre": "Internet", "fecha": "05/11/2026", "faltan": "7 días", "monto": cop(90000)},
    {"nombre": "Cuota de la moto", "fecha": "10/11/2026", "faltan": "12 días", "monto": cop(210000)},
]

MESES = [
    {"mes": "Agosto", "ingresos": 1800000, "gastos": 1250000},
    {"mes": "Septiembre", "ingresos": 1950000, "gastos": 1400000},
    {"mes": "Octubre", "ingresos": 1950000, "gastos": 890000},
]


def inicio(request):
    return render(request, "core/inicio.html")


def login(request):
    return render(request, "core/login.html")


def registro(request):
    return render(request, "core/registro.html")


def panel(request):
    contexto = {
        "disponible": cop(300000),
        "para_gastos": cop(700000),
        "ahorro": cop(200000),
        "meta_principal": METAS[0],
        "pagos": PAGOS,
    }
    return render(request, "core/panel.html", contexto)


def ingresos(request):
    return render(request, "core/ingresos.html", {"ingresos": INGRESOS})


def gastos(request):
    return render(request, "core/gastos.html", {"gastos": GASTOS})


def metas(request):
    return render(request, "core/metas.html", {"metas": METAS})


def recordatorios(request):
    return render(request, "core/recordatorios.html", {"pagos": PAGOS})


def reportes(request):
    mayor = max(max(m["ingresos"], m["gastos"]) for m in MESES)
    filas = []
    for m in MESES:
        filas.append({
            "mes": m["mes"],
            "ingresos": cop(m["ingresos"]),
            "gastos": cop(m["gastos"]),
            "ancho_ingresos": round(m["ingresos"] * 100 / mayor),
            "ancho_gastos": round(m["gastos"] * 100 / mayor),
        })
    return render(request, "core/reportes.html", {"filas": filas})
