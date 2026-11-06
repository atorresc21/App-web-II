from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import (
    authenticate,
    logout,
    get_user_model,
    login as auth_login
)
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Sum


from .models import Ingreso, Gasto, Meta, Recordatorio
from .forms import IngresoForm, GastoForm, MetaForm, RecordatorioForm




# Formato de pesos colombianos
def cop(valor):
    return "$ {:,.0f}".format(valor or 0).replace(",", ".")




# ==================================================
# PÁGINAS PRINCIPALES
# ==================================================


def inicio(request):
    return render(request, "core/inicio.html")




# ==================================================
# INICIAR SESIÓN
# ==================================================


def login(request):
    if request.user.is_authenticated:
        return redirect("panel")


    if request.method == "POST":
        correo = request.POST.get("correo", "").strip().lower()
        clave = request.POST.get("clave", "")


        Usuario = get_user_model()


        usuario = Usuario.objects.filter(
            email__iexact=correo
        ).first()


        if usuario:
            usuario_autenticado = authenticate(
                request,
                username=usuario.get_username(),
                password=clave
            )


            if usuario_autenticado is not None:
                auth_login(request, usuario_autenticado)
                return redirect("panel")


        return render(request, "core/login.html", {
            "error": "Correo electrónico o contraseña incorrectos."
        })


    return render(request, "core/login.html")




# ==================================================
# REGISTRO DE USUARIOS
# ==================================================


def registro(request):
    if request.user.is_authenticated:
        return redirect("panel")


    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        correo = request.POST.get("correo", "").strip().lower()
        clave = request.POST.get("clave", "")
        privacidad = request.POST.get("privacidad")


        Usuario = get_user_model()


        if not privacidad:
            return render(request, "core/registro.html", {
                "error": "Debes aceptar el aviso de privacidad."
            })


        if not nombre or not correo or not clave:
            return render(request, "core/registro.html", {
                "error": "Todos los campos son obligatorios."
            })


        if len(correo) > 150:
            return render(request, "core/registro.html", {
                "error": "El correo electrónico es demasiado largo."
            })


        if Usuario.objects.filter(email__iexact=correo).exists():
            return render(request, "core/registro.html", {
                "error": "Este correo electrónico ya está registrado."
            })


        if Usuario.objects.filter(username=correo).exists():
            return render(request, "core/registro.html", {
                "error": "No se puede utilizar este correo. Intenta con otro."
            })


        nuevo_usuario = Usuario(
            username=correo,
            email=correo,
            first_name=nombre
        )


        try:
            validate_password(clave, user=nuevo_usuario)
        except ValidationError as error:
            return render(request, "core/registro.html", {
                "error": " ".join(error.messages)
            })


        Usuario.objects.create_user(
            username=correo,
            email=correo,
            password=clave,
            first_name=nombre
        )


        return redirect("login")


    return render(request, "core/registro.html")




# ==================================================
# CERRAR SESIÓN
# ==================================================


@login_required
def cerrar_sesion(request):
    if request.method == "POST":
        logout(request)
        return redirect("inicio")


    return redirect("panel")




# ==================================================
# PANEL PRINCIPAL
# ==================================================


@login_required
def panel(request):
    ingresos = Ingreso.objects.filter(usuario=request.user)
    gastos = Gasto.objects.filter(usuario=request.user)


    total_ingresos = ingresos.aggregate(
        total=Sum("monto")
    )["total"] or 0


    total_gastos = gastos.aggregate(
        total=Sum("monto")
    )["total"] or 0


    meta_principal = Meta.objects.filter(
        usuario=request.user,
        principal=True
    ).first()


    pagos = Recordatorio.objects.filter(
        usuario=request.user
    )


    contexto = {
        "disponible": cop(total_ingresos - total_gastos),
        "para_gastos": cop(total_gastos),
        "ahorro": cop(
            meta_principal.ahorrado if meta_principal else 0
        ),
        "meta_principal": meta_principal,
        "pagos": pagos,
    }


    return render(request, "core/panel.html", contexto)




# ==================================================
# INGRESOS
# ==================================================


@login_required
def ingresos(request):
    datos = Ingreso.objects.filter(usuario=request.user)


    return render(request, "core/ingresos.html", {
        "ingresos": datos
    })




@login_required
def crear_ingreso(request):
    formulario = IngresoForm(request.POST or None)


    if request.method == "POST" and formulario.is_valid():
        nuevo = formulario.save(commit=False)
        nuevo.usuario = request.user
        nuevo.save()


        return redirect("ingresos")


    return render(request, "core/formulario.html", {
        "formulario": formulario,
        "titulo": "Registrar ingreso",
        "volver_url": "ingresos"
    })




@login_required
def editar_ingreso(request, pk):
    ingreso = get_object_or_404(
        Ingreso, pk=pk, usuario=request.user
    )


    formulario = IngresoForm(
        request.POST or None,
        instance=ingreso
    )


    if request.method == "POST" and formulario.is_valid():
        formulario.save()
        return redirect("ingresos")


    return render(request, "core/formulario.html", {
        "formulario": formulario,
        "titulo": "Editar ingreso",
        "volver_url": "ingresos"
    })




@login_required
def eliminar_ingreso(request, pk):
    ingreso = get_object_or_404(
        Ingreso, pk=pk, usuario=request.user
    )


    if request.method == "POST":
        ingreso.delete()
        return redirect("ingresos")


    return render(request, "core/confirmar_eliminacion.html", {
        "objeto": ingreso,
        "volver_url": "ingresos"
    })




# ==================================================
# GASTOS
# ==================================================


@login_required
def gastos(request):
    datos = Gasto.objects.filter(usuario=request.user)


    return render(request, "core/gastos.html", {
        "gastos": datos
    })




@login_required
def crear_gasto(request):
    formulario = GastoForm(request.POST or None)


    if request.method == "POST" and formulario.is_valid():
        nuevo = formulario.save(commit=False)
        nuevo.usuario = request.user
        nuevo.save()


        return redirect("gastos")


    return render(request, "core/formulario.html", {
        "formulario": formulario,
        "titulo": "Registrar gasto",
        "volver_url": "gastos"
    })




@login_required
def editar_gasto(request, pk):
    gasto = get_object_or_404(
        Gasto, pk=pk, usuario=request.user
    )


    formulario = GastoForm(
        request.POST or None,
        instance=gasto
    )


    if request.method == "POST" and formulario.is_valid():
        formulario.save()
        return redirect("gastos")


    return render(request, "core/formulario.html", {
        "formulario": formulario,
        "titulo": "Editar gasto",
        "volver_url": "gastos"
    })




@login_required
def eliminar_gasto(request, pk):
    gasto = get_object_or_404(
        Gasto, pk=pk, usuario=request.user
    )


    if request.method == "POST":
        gasto.delete()
        return redirect("gastos")


    return render(request, "core/confirmar_eliminacion.html", {
        "objeto": gasto,
        "volver_url": "gastos"
    })




# ==================================================
# METAS
# ==================================================


@login_required
def metas(request):
    datos = Meta.objects.filter(usuario=request.user)


    return render(request, "core/metas.html", {
        "metas": datos
    })




@login_required
def crear_meta(request):
    formulario = MetaForm(request.POST or None)


    if request.method == "POST" and formulario.is_valid():
        nueva = formulario.save(commit=False)
        nueva.usuario = request.user
        nueva.save()


        return redirect("metas")


    return render(request, "core/formulario.html", {
        "formulario": formulario,
        "titulo": "Crear meta de ahorro",
        "volver_url": "metas"
    })




@login_required
def editar_meta(request, pk):
    meta = get_object_or_404(
        Meta, pk=pk, usuario=request.user
    )


    formulario = MetaForm(
        request.POST or None,
        instance=meta
    )


    if request.method == "POST" and formulario.is_valid():
        formulario.save()
        return redirect("metas")


    return render(request, "core/formulario.html", {
        "formulario": formulario,
        "titulo": "Editar meta",
        "volver_url": "metas"
    })




@login_required
def eliminar_meta(request, pk):
    meta = get_object_or_404(
        Meta, pk=pk, usuario=request.user
    )


    if request.method == "POST":
        meta.delete()
        return redirect("metas")


    return render(request, "core/confirmar_eliminacion.html", {
        "objeto": meta,
        "volver_url": "metas"
    })




# ==================================================
# RECORDATORIOS
# ==================================================


@login_required
def recordatorios(request):
    datos = Recordatorio.objects.filter(
        usuario=request.user
    )


    return render(request, "core/recordatorios.html", {
        "pagos": datos
    })




@login_required
def crear_recordatorio(request):
    formulario = RecordatorioForm(request.POST or None)


    if request.method == "POST" and formulario.is_valid():
        nuevo = formulario.save(commit=False)
        nuevo.usuario = request.user
        nuevo.save()


        return redirect("recordatorios")


    return render(request, "core/formulario.html", {
        "formulario": formulario,
        "titulo": "Crear recordatorio",
        "volver_url": "recordatorios"
    })




@login_required
def editar_recordatorio(request, pk):
    recordatorio = get_object_or_404(
        Recordatorio, pk=pk, usuario=request.user
    )


    formulario = RecordatorioForm(
        request.POST or None,
        instance=recordatorio
    )


    if request.method == "POST" and formulario.is_valid():
        formulario.save()
        return redirect("recordatorios")


    return render(request, "core/formulario.html", {
        "formulario": formulario,
        "titulo": "Editar recordatorio",
        "volver_url": "recordatorios"
    })




@login_required
def eliminar_recordatorio(request, pk):
    recordatorio = get_object_or_404(
        Recordatorio, pk=pk, usuario=request.user
    )


    if request.method == "POST":
        recordatorio.delete()
        return redirect("recordatorios")


    return render(request, "core/confirmar_eliminacion.html", {
        "objeto": recordatorio,
        "volver_url": "recordatorios"
    })




# ==================================================
# REPORTES
# ==================================================


@login_required
def reportes(request):
    ingresos = Ingreso.objects.filter(usuario=request.user)
    gastos = Gasto.objects.filter(usuario=request.user)


    total_ingresos = ingresos.aggregate(
        total=Sum("monto")
    )["total"] or 0


    total_gastos = gastos.aggregate(
        total=Sum("monto")
    )["total"] or 0


    mayor = max(total_ingresos, total_gastos)


    filas = [{
        "mes": "Total",
        "ingresos": cop(total_ingresos),
        "gastos": cop(total_gastos),
        "ancho_ingresos": round(
            total_ingresos * 100 / mayor
        ) if mayor else 0,
        "ancho_gastos": round(
            total_gastos * 100 / mayor
        ) if mayor else 0,
    }]


    return render(request, "core/reportes.html", {
        "filas": filas
    })