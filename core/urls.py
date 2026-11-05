from django.urls import path

from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("login/", views.login, name="login"),
    path("registro/", views.registro, name="registro"),
    path("panel/", views.panel, name="panel"),
    path("ingresos/", views.ingresos, name="ingresos"),
    path("gastos/", views.gastos, name="gastos"),
    path("metas/", views.metas, name="metas"),
    path("recordatorios/", views.recordatorios, name="recordatorios"),
    path("reportes/", views.reportes, name="reportes"),
]
