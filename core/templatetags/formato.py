from django import template
from django.utils import timezone

from ..utilidades import cop as formato_cop

register = template.Library()


@register.filter(name="cop")
def cop_filtro(valor):
    """{{ monto|cop }} -> $ 1.200.000"""
    return formato_cop(valor)


@register.filter
def faltan(fecha):
    """{{ fecha|faltan }} -> hoy, mañana, en 3 días, ya venció"""
    dias = (fecha - timezone.localdate()).days
    if dias < 0:
        return "ya venció"
    if dias == 0:
        return "hoy"
    if dias == 1:
        return "mañana"
    return f"en {dias} días"
