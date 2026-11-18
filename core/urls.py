from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import AccesoForm

urlpatterns = [
    path("", views.inicio, name="inicio"),

    # Cuentas
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="core/login.html",
            authentication_form=AccesoForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("salir/", auth_views.LogoutView.as_view(), name="logout"),
    path("registro/", views.registro, name="registro"),

    # Panel y reportes
    path("panel/", views.panel, name="panel"),
    path("reportes/", views.reportes, name="reportes"),

    # Ingresos
    path("ingresos/", views.IngresoLista.as_view(), name="ingresos"),
    path("ingresos/nuevo/", views.IngresoCrear.as_view(), name="ingreso_nuevo"),
    path("ingresos/<int:pk>/editar/", views.IngresoEditar.as_view(), name="ingreso_editar"),
    path("ingresos/<int:pk>/eliminar/", views.IngresoEliminar.as_view(), name="ingreso_eliminar"),

    # Gastos
    path("gastos/", views.GastoLista.as_view(), name="gastos"),
    path("gastos/nuevo/", views.GastoCrear.as_view(), name="gasto_nuevo"),
    path("gastos/<int:pk>/editar/", views.GastoEditar.as_view(), name="gasto_editar"),
    path("gastos/<int:pk>/eliminar/", views.GastoEliminar.as_view(), name="gasto_eliminar"),

    # Metas
    path("metas/", views.MetaLista.as_view(), name="metas"),
    path("metas/nueva/", views.MetaCrear.as_view(), name="meta_nueva"),
    path("metas/<int:pk>/editar/", views.MetaEditar.as_view(), name="meta_editar"),
    path("metas/<int:pk>/eliminar/", views.MetaEliminar.as_view(), name="meta_eliminar"),

    # Recordatorios
    path("recordatorios/", views.RecordatorioLista.as_view(), name="recordatorios"),
    path("recordatorios/nuevo/", views.RecordatorioCrear.as_view(), name="recordatorio_nuevo"),
    path("recordatorios/<int:pk>/editar/", views.RecordatorioEditar.as_view(), name="recordatorio_editar"),
    path("recordatorios/<int:pk>/eliminar/", views.RecordatorioEliminar.as_view(), name="recordatorio_eliminar"),

    # Administración (solo rol Administrador)
    path("administracion/", views.usuarios_admin, name="usuarios_admin"),
    path("administracion/usuarios/<int:pk>/estado/", views.usuario_estado, name="usuario_estado"),
]
