
import pytest
from datetime import date
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Ingreso, Gasto, Meta, Recordatorio


@pytest.fixture
def usuario():
    Usuario = get_user_model()
    return Usuario.objects.create_user(
        username="carlos",
        email="carlos@gmail.com",
        password="ClaveSegura123!"
    )


@pytest.fixture
def otro_usuario():
    Usuario = get_user_model()
    return Usuario.objects.create_user(
        username="jesus",
        email="jesus@gmail.com",
        password="ClaveSegura123!"
    )


# ==========================================
# PRUEBAS DE AUTENTICACIÓN
# ==========================================

@pytest.mark.django_db
def test_usuario_sin_sesion_no_puede_entrar_al_panel(client):
    respuesta = client.get(reverse("panel"))

    assert respuesta.status_code == 302


@pytest.mark.django_db
def test_usuario_puede_iniciar_sesion(client, usuario):
    respuesta = client.post(reverse("login"), {
        "correo": "carlos@gmail.com",
        "clave": "ClaveSegura123!"
    })

    assert respuesta.status_code == 302
    assert respuesta.url == reverse("panel")


@pytest.mark.django_db
def test_login_rechaza_contrasena_incorrecta(client, usuario):
    respuesta = client.post(reverse("login"), {
        "correo": "carlos@gmail.com",
        "clave": "incorrecta"
    })

    assert respuesta.status_code == 200
    assert "error" in respuesta.context


# ==========================================
# PRUEBAS DE SEGURIDAD
# ==========================================

@pytest.mark.django_db
@pytest.mark.parametrize("nombre_ruta", [
    "panel",
    "ingresos",
    "gastos",
    "metas",
    "recordatorios",
    "reportes",
])
def test_paginas_privadas_requieren_inicio_sesion(client, nombre_ruta):
    respuesta = client.get(reverse(nombre_ruta))

    assert respuesta.status_code == 302


@pytest.mark.django_db
def test_usuario_no_puede_editar_ingreso_de_otro(
    client, usuario, otro_usuario
):
    ingreso = Ingreso.objects.create(
        usuario=otro_usuario,
        descripcion="Ingreso de Jesus",
        monto=500000,
        fecha=date.today(),
        periodicidad="quincenal"
    )

    client.force_login(usuario)

    respuesta = client.get(
        reverse("editar_ingreso", args=[ingreso.pk])
    )

    assert respuesta.status_code == 404


@pytest.mark.django_db
def test_usuario_no_puede_eliminar_gasto_de_otro(
    client, usuario, otro_usuario
):
    gasto = Gasto.objects.create(
        usuario=otro_usuario,
        descripcion="Gasto de Jesus",
        monto=100000,
        fecha=date.today(),
        categoria="vivienda",
        tipo="fijo"
    )

    client.force_login(usuario)

    respuesta = client.get(
        reverse("eliminar_gasto", args=[gasto.pk])
    )

    assert respuesta.status_code == 404
    assert Gasto.objects.filter(pk=gasto.pk).exists()


@pytest.mark.django_db
def test_usuario_no_puede_editar_meta_de_otro(
    client, usuario, otro_usuario
):
    meta = Meta.objects.create(
        usuario=otro_usuario,
        nombre="Meta de Jesus",
        objetivo=1000000,
        ahorrado=200000
    )

    client.force_login(usuario)

    respuesta = client.get(
        reverse("editar_meta", args=[meta.pk])
    )

    assert respuesta.status_code == 404


@pytest.mark.django_db
def test_usuario_no_puede_eliminar_recordatorio_de_otro(
    client, usuario, otro_usuario
):
    recordatorio = Recordatorio.objects.create(
        usuario=otro_usuario,
        nombre="Pago de Jesus",
        monto=50000,
        fecha=date.today()
    )

    client.force_login(usuario)

    respuesta = client.get(
        reverse("eliminar_recordatorio", args=[recordatorio.pk])
    )

    assert respuesta.status_code == 404
    assert Recordatorio.objects.filter(pk=recordatorio.pk).exists()
