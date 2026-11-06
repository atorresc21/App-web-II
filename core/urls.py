from django.urls import path
from . import views




urlpatterns = [


    # Páginas principales
    path("", views.inicio, name="inicio"),
    path("login/", views.login, name="login"),
    path("registro/", views.registro, name="registro"),
    path("cerrar-sesion/", views.cerrar_sesion, name="cerrar_sesion"),


    # Panel
    path("panel/", views.panel, name="panel"),


    # Ingresos
    path("ingresos/", views.ingresos, name="ingresos"),
    path("ingresos/crear/", views.crear_ingreso, name="crear_ingreso"),
    path("ingresos/editar/<int:pk>/", views.editar_ingreso, name="editar_ingreso"),
    path("ingresos/eliminar/<int:pk>/", views.eliminar_ingreso, name="eliminar_ingreso"),


    # Gastos
    path("gastos/", views.gastos, name="gastos"),
    path("gastos/crear/", views.crear_gasto, name="crear_gasto"),
    path("gastos/editar/<int:pk>/", views.editar_gasto, name="editar_gasto"),
    path("gastos/eliminar/<int:pk>/", views.eliminar_gasto, name="eliminar_gasto"),


    # Metas
    path("metas/", views.metas, name="metas"),
    path("metas/crear/", views.crear_meta, name="crear_meta"),
    path("metas/editar/<int:pk>/", views.editar_meta, name="editar_meta"),
    path("metas/eliminar/<int:pk>/", views.eliminar_meta, name="eliminar_meta"),


    # Recordatorios
    path("recordatorios/", views.recordatorios, name="recordatorios"),
    path("recordatorios/crear/", views.crear_recordatorio, name="crear_recordatorio"),
    path("recordatorios/editar/<int:pk>/", views.editar_recordatorio, name="editar_recordatorio"),
    path("recordatorios/eliminar/<int:pk>/", views.eliminar_recordatorio, name="eliminar_recordatorio"),


    # Reportes
    path("reportes/", views.reportes, name="reportes"),


]