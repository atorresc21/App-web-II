
from datetime import timedelta

import pytest
from django.utils import timezone

from core.forms import (
    IngresoForm,
    GastoForm,
    MetaForm,
    RecordatorioForm,
)

def test_ingreso_formulario_valido():
    formulario = IngresoForm(data={
        "descripcion": "Salario",
        "monto": "1500000",
        "fecha": timezone.localdate().isoformat(),
        "periodicidad": "quincenal",
    })

    assert formulario.is_valid()

def test_ingreso_rechaza_monto_cero():
    formulario = IngresoForm(data={
        "descripcion": "Salario",
        "monto": "0",
        "fecha": timezone.localdate().isoformat(),
        "periodicidad": "quincenal",
    })

    assert not formulario.is_valid()
    assert "monto" in formulario.errors

def test_ingreso_rechaza_fecha_futura():
    fecha_futura = timezone.localdate() + timedelta(days=1)

    formulario = IngresoForm(data={
        "descripcion": "Salario",
        "monto": "1500000",
        "fecha": fecha_futura.isoformat(),
        "periodicidad": "quincenal",
    })

    assert not formulario.is_valid()
    assert "fecha" in formulario.errors

def test_gasto_formulario_valido():
    formulario = GastoForm(data={
        "descripcion": "Mercado",
        "monto": "50000",
        "fecha": timezone.localdate().isoformat(),
        "categoria": "alimentacion",
        "tipo": "variable",
    })

    assert formulario.is_valid()

def test_gasto_rechaza_monto_negativo():
    formulario = GastoForm(data={
        "descripcion": "Mercado",
        "monto": "-50000",
        "fecha": timezone.localdate().isoformat(),
        "categoria": "alimentacion",
        "tipo": "variable",
    })

    assert not formulario.is_valid()
    assert "monto" in formulario.errors

def test_meta_formulario_valido():
    formulario = MetaForm(data={
        "nombre": "Comprar computador",
        "objetivo": "2000000",
        "ahorrado": "500000",
        "principal": True,
    })

    assert formulario.is_valid()

def test_meta_rechaza_objetivo_cero():
    formulario = MetaForm(data={
        "nombre": "Comprar computador",
        "objetivo": "0",
        "ahorrado": "0",
        "principal": False,
    })

    assert not formulario.is_valid()
    assert "objetivo" in formulario.errors

def test_meta_rechaza_ahorro_superior_al_objetivo():
    formulario = MetaForm(data={
        "nombre": "Comprar computador",
        "objetivo": "1000000",
        "ahorrado": "1500000",
        "principal": False,
    })

    assert not formulario.is_valid()

def test_recordatorio_formulario_valido():
    formulario = RecordatorioForm(data={
        "nombre": "Pago de internet",
        "monto": "80000",
        "fecha": timezone.localdate().isoformat(),
    })

    assert formulario.is_valid()

def test_recordatorio_rechaza_monto_cero():
    formulario = RecordatorioForm(data={
        "nombre": "Pago de internet",
        "monto": "0",
        "fecha": timezone.localdate().isoformat(),
    })

    assert not formulario.is_valid()
    assert "monto" in formulario.errors

def test_recordatorio_rechaza_fecha_pasada():
    fecha_pasada = timezone.localdate() - timedelta(days=1)

    formulario = RecordatorioForm(data={
        "nombre": "Pago de internet",
        "monto": "80000",
        "fecha": fecha_pasada.isoformat(),
    })

    assert not formulario.is_valid()
    assert "fecha" in formulario.errors