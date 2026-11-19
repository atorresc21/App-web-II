from collections import defaultdict

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login as iniciar_sesion
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import GastoForm, IngresoForm, MetaForm, RecordatorioForm, RegistroForm
from .models import Gasto, Ingreso, Recordatorio
from .models import Meta as MetaAhorro
from .utilidades import NOMBRES_MES, calcular_plan, cop, inicio_periodo, movimientos

Usuario = get_user_model()


# ---------------------------------------------------------------------------
# Páginas generales y cuentas
# ---------------------------------------------------------------------------

def inicio(request):
    return render(request, "core/inicio.html")


def registro(request):
    if request.user.is_authenticated:
        return redirect("panel")
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.guardar()
            iniciar_sesion(request, usuario)
            messages.success(request, f"Bienvenido a Axon Budget, {usuario.first_name}. Tu cuenta está lista.")
            return redirect("panel")
    else:
        form = RegistroForm()
    return render(request, "core/registro.html", {"form": form})


# ---------------------------------------------------------------------------
# Panel
# ---------------------------------------------------------------------------

@login_required
def panel(request):
    hoy = timezone.localdate()
    plan = calcular_plan(request.user, hoy)

    metas = MetaAhorro.objects.filter(usuario=request.user)
    meta_principal = metas.filter(principal=True).first() or metas.first()

    proximos = list(Recordatorio.objects.filter(usuario=request.user, fecha__gte=hoy)[:4])
    alertas = [r for r in proximos if (r.fecha - hoy).days <= 3]

    contexto = {
        "mes_actual": f"{NOMBRES_MES[hoy.month - 1].capitalize()} {hoy.year}",
        "plan": plan,
        "meta_principal": meta_principal,
        "proximos": proximos,
        "alertas": alertas,
        "recientes": movimientos(request.user)[:5],
    }
    return render(request, "core/panel.html", contexto)


# ---------------------------------------------------------------------------
# Ingresos, gastos, metas y recordatorios (crear, consultar, editar, eliminar)
# Cada persona solo ve y modifica sus propios registros.
# ---------------------------------------------------------------------------

class DelUsuario(LoginRequiredMixin):
    def get_queryset(self):
        return super().get_queryset().filter(usuario=self.request.user)


class FechaHoy:
    """Al crear, la fecha aparece con el día de hoy."""

    def get_initial(self):
        inicial = super().get_initial()
        inicial["fecha"] = timezone.localdate()
        return inicial


class Formulario(DelUsuario):
    template_name = "core/formulario.html"
    titulo = ""
    boton = "Guardar"
    mensaje = "Cambios guardados."
    destino = "panel"
    cancelar = None

    def mensaje_exito(self):
        return self.mensaje

    def get_success_url(self):
        return reverse(self.destino)

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["titulo"] = self.titulo
        contexto["boton"] = self.boton
        contexto["cancelar"] = reverse(self.cancelar or self.destino)
        return contexto

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        respuesta = super().form_valid(form)
        messages.success(self.request, self.mensaje_exito())
        return respuesta


class Eliminar(DelUsuario, DeleteView):
    template_name = "core/confirmar_eliminar.html"
    destino = "panel"
    mensaje = "Registro eliminado."

    def get_success_url(self):
        return reverse(self.destino)

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["cancelar"] = reverse(self.destino)
        return contexto

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        messages.success(self.request, self.mensaje)
        return respuesta


# --- Ingresos ---------------------------------------------------------------

class IngresoLista(DelUsuario, ListView):
    model = Ingreso
    template_name = "core/ingresos.html"
    context_object_name = "ingresos"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["total"] = sum(i.monto for i in contexto["ingresos"])
        return contexto


class IngresoCrear(FechaHoy, Formulario, CreateView):
    model = Ingreso
    form_class = IngresoForm
    titulo = "Nuevo ingreso"
    boton = "Guardar ingreso"
    destino = "panel"
    cancelar = "ingresos"

    def mensaje_exito(self):
        # Regla de negocio: cada ingreso nuevo recalcula el plan del mes.
        plan = calcular_plan(self.request.user)
        return (
            f"Ingreso guardado. Este mes separa {cop(plan['gastos'])} para tus gastos, "
            f"ahorra {cop(plan['ahorro'])} y te quedan {cop(plan['disponible'])} disponibles."
        )


class IngresoEditar(Formulario, UpdateView):
    model = Ingreso
    form_class = IngresoForm
    titulo = "Editar ingreso"
    destino = "ingresos"
    mensaje = "Ingreso actualizado."


class IngresoEliminar(Eliminar):
    model = Ingreso
    destino = "ingresos"
    mensaje = "Ingreso eliminado."


# --- Gastos -----------------------------------------------------------------

class GastoLista(DelUsuario, ListView):
    model = Gasto
    template_name = "core/gastos.html"
    context_object_name = "gastos"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["total"] = sum(g.monto for g in contexto["gastos"])
        return contexto


class GastoCrear(FechaHoy, Formulario, CreateView):
    model = Gasto
    form_class = GastoForm
    titulo = "Nuevo gasto"
    boton = "Guardar gasto"
    destino = "gastos"
    mensaje = "Gasto guardado."


class GastoEditar(Formulario, UpdateView):
    model = Gasto
    form_class = GastoForm
    titulo = "Editar gasto"
    destino = "gastos"
    mensaje = "Gasto actualizado."


class GastoEliminar(Eliminar):
    model = Gasto
    destino = "gastos"
    mensaje = "Gasto eliminado."


# --- Metas ------------------------------------------------------------------

class MetaLista(DelUsuario, ListView):
    model = MetaAhorro
    template_name = "core/metas.html"
    context_object_name = "metas"

    def get_queryset(self):
        return super().get_queryset().order_by("-principal", "nombre")


class MetaCrear(Formulario, CreateView):
    model = MetaAhorro
    form_class = MetaForm
    titulo = "Nueva meta"
    boton = "Guardar meta"
    destino = "metas"
    mensaje = "Meta guardada."


class MetaEditar(Formulario, UpdateView):
    model = MetaAhorro
    form_class = MetaForm
    titulo = "Editar meta"
    destino = "metas"
    mensaje = "Meta actualizada."


class MetaEliminar(Eliminar):
    model = MetaAhorro
    destino = "metas"
    mensaje = "Meta eliminada."


# --- Recordatorios ----------------------------------------------------------

class RecordatorioLista(DelUsuario, ListView):
    model = Recordatorio
    template_name = "core/recordatorios.html"
    context_object_name = "pagos"


class RecordatorioCrear(FechaHoy, Formulario, CreateView):
    model = Recordatorio
    form_class = RecordatorioForm
    titulo = "Nuevo recordatorio de pago"
    boton = "Guardar recordatorio"
    destino = "recordatorios"
    mensaje = "Recordatorio guardado."


class RecordatorioEditar(Formulario, UpdateView):
    model = Recordatorio
    form_class = RecordatorioForm
    titulo = "Editar recordatorio"
    destino = "recordatorios"
    mensaje = "Recordatorio actualizado."


class RecordatorioEliminar(Eliminar):
    model = Recordatorio
    destino = "recordatorios"
    mensaje = "Recordatorio eliminado."


# ---------------------------------------------------------------------------
# Reportes e historial
# ---------------------------------------------------------------------------

@login_required
def reportes(request):
    hoy = timezone.localdate()

    periodo = request.GET.get("periodo", "mes")
    if periodo not in ("semana", "quincena", "mes", "todo"):
        periodo = "mes"
    lista = movimientos(request.user, inicio_periodo(periodo, hoy))
    total_ingresos = sum(m["monto"] for m in lista if m["tipo"] == "Ingreso")
    total_gastos = sum(m["monto"] for m in lista if m["tipo"] == "Gasto")

    # Ingresos y gastos de los últimos seis meses.
    meses = []
    anio, mes = hoy.year, hoy.month
    for _ in range(6):
        meses.append((anio, mes))
        mes -= 1
        if mes == 0:
            mes, anio = 12, anio - 1
    meses.reverse()
    desde = hoy.replace(year=meses[0][0], month=meses[0][1], day=1)

    ingresos_mes = defaultdict(int)
    gastos_mes = defaultdict(int)
    for fecha, monto in Ingreso.objects.filter(usuario=request.user, fecha__gte=desde).values_list("fecha", "monto"):
        ingresos_mes[(fecha.year, fecha.month)] += int(monto)
    for fecha, monto in Gasto.objects.filter(usuario=request.user, fecha__gte=desde).values_list("fecha", "monto"):
        gastos_mes[(fecha.year, fecha.month)] += int(monto)

    mayor = max(list(ingresos_mes.values()) + list(gastos_mes.values()) + [1])
    filas = []
    for anio, mes in meses:
        ing = ingresos_mes[(anio, mes)]
        gas = gastos_mes[(anio, mes)]
        filas.append({
            "mes": f"{NOMBRES_MES[mes - 1].capitalize()} {anio}",
            "ingresos": ing,
            "gastos": gas,
            "ancho_ingresos": round(ing * 100 / mayor),
            "ancho_gastos": round(gas * 100 / mayor),
        })

    # Gastos del mes actual por categoría.
    nombres = dict(Gasto.CATEGORIAS)
    por_categoria = defaultdict(int)
    for categoria, monto in Gasto.objects.filter(
        usuario=request.user, fecha__year=hoy.year, fecha__month=hoy.month
    ).values_list("categoria", "monto"):
        por_categoria[categoria] += int(monto)
    mayor_cat = max(list(por_categoria.values()) + [1])
    categorias = [
        {"nombre": nombres.get(c, c), "monto": m, "ancho": round(m * 100 / mayor_cat)}
        for c, m in sorted(por_categoria.items(), key=lambda par: par[1], reverse=True)
    ]

    contexto = {
        "periodo": periodo,
        "movimientos": lista,
        "total_ingresos": total_ingresos,
        "total_gastos": total_gastos,
        "balance": total_ingresos - total_gastos,
        "filas": filas,
        "categorias": categorias,
        "mes_actual": f"{NOMBRES_MES[hoy.month - 1].capitalize()} {hoy.year}",
    }
    return render(request, "core/reportes.html", contexto)


# ---------------------------------------------------------------------------
# Rol Administrador
# ---------------------------------------------------------------------------

@login_required
def usuarios_admin(request):
    if not request.user.is_staff:
        raise PermissionDenied
    usuarios = Usuario.objects.order_by("-date_joined")
    contexto = {
        "usuarios": usuarios,
        "total": usuarios.count(),
        "activos": usuarios.filter(is_active=True).count(),
    }
    return render(request, "core/usuarios_admin.html", contexto)


@login_required
@require_POST
def usuario_estado(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied
    objetivo = get_object_or_404(Usuario, pk=pk)
    if objetivo == request.user or objetivo.is_superuser:
        messages.error(request, "No puedes desactivar esa cuenta.")
    else:
        objetivo.is_active = not objetivo.is_active
        objetivo.save(update_fields=["is_active"])
        estado = "activada" if objetivo.is_active else "desactivada"
        messages.success(request, f"La cuenta de {objetivo.first_name or objetivo.username} fue {estado}.")
    return redirect("usuarios_admin")
