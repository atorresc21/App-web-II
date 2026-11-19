
from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from core.models import Ingreso, Gasto, Meta, Recordatorio


Usuario = get_user_model()


@pytest.fixture
def usuario(db):
    return Usuario.objects.create_user(
        username="prueba@correo.com",
        email="prueba@correo.com",
        password="Prueba123456"
    )


@pytest.mark.django_db
def test_crear_ingreso(usuario):
    ingreso = Ingreso.objects.create(
        usuario=usuario,
        descripcion="Salario",
        monto=Decimal("1500000"),
        fecha=date.today()
    )

    assert ingreso.descripcion == "Salario"
    assert ingreso.monto == Decimal("1500000")
    assert ingreso.periodicidad == "quincenal"


@pytest.mark.django_db
def test_crear_gasto(usuario):
    gasto = Gasto.objects.create(
        usuario=usuario,
        descripcion="Alimentación",
        monto=Decimal("50000"),
        fecha=date.today()
    )

    assert gasto.descripcion == "Alimentación"
    assert gasto.categoria == "otros"
    assert gasto.tipo == "variable"


@pytest.mark.django_db
def test_avance_meta(usuario):
    meta = Meta.objects.create(
        usuario=usuario,
        nombre="Comprar computador",
        objetivo=Decimal("2000000"),
        ahorrado=Decimal("1000000")
    )

    assert meta.avance() == 50


@pytest.mark.django_db
def test_avance_meta_no_supera_100(usuario):
    meta = Meta.objects.create(
        usuario=usuario,
        nombre="Viaje",
        objetivo=Decimal("1000000"),
        ahorrado=Decimal("1500000")
    )

    assert meta.avance() == 100


@pytest.mark.django_db
def test_solo_una_meta_principal_por_usuario(usuario):
    primera = Meta.objects.create(
        usuario=usuario,
        nombre="Primera meta",
        objetivo=Decimal("1000000"),
        principal=True
    )

    segunda = Meta.objects.create(
        usuario=usuario,
        nombre="Segunda meta",
        objetivo=Decimal("2000000"),
        principal=True
    )

    primera.refresh_from_db()

    assert primera.principal is False
    assert segunda.principal is True


@pytest.mark.django_db
def test_crear_recordatorio(usuario):
    recordatorio = Recordatorio.objects.create(
        usuario=usuario,
        nombre="Pago de internet",
        monto=Decimal("80000"),
        fecha=date.today()
    )

    assert recordatorio.nombre == "Pago de internet"
    assert recordatorio.monto == Decimal("80000")
