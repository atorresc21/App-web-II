from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Gasto, Ingreso, Recordatorio
from .models import Meta as MetaAhorro

Usuario = get_user_model()


def _campo_fecha():
    return forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")


class MontoPositivoMixin:
    def clean_monto(self):
        monto = self.cleaned_data["monto"]
        if monto <= 0:
            raise ValidationError("El monto debe ser mayor que cero.")
        return monto


class FechaNoFuturaMixin:
    def clean_fecha(self):
        fecha = self.cleaned_data["fecha"]
        if fecha > timezone.localdate():
            raise ValidationError("La fecha no puede ser futura.")
        return fecha


class IngresoForm(MontoPositivoMixin, FechaNoFuturaMixin, forms.ModelForm):
    class Meta:
        model = Ingreso
        fields = ["descripcion", "monto", "fecha", "periodicidad"]
        labels = {
            "descripcion": "Descripción",
            "monto": "Monto (en pesos)",
            "fecha": "Fecha",
            "periodicidad": "Periodicidad",
        }
        widgets = {
            "descripcion": forms.TextInput(attrs={"placeholder": "Ej.: Pago quincenal"}),
            "fecha": _campo_fecha(),
        }


class GastoForm(MontoPositivoMixin, FechaNoFuturaMixin, forms.ModelForm):
    class Meta:
        model = Gasto
        fields = ["descripcion", "monto", "fecha", "categoria", "tipo"]
        labels = {
            "descripcion": "Descripción",
            "monto": "Monto (en pesos)",
            "fecha": "Fecha",
            "categoria": "Categoría",
            "tipo": "Tipo de gasto",
        }
        widgets = {
            "descripcion": forms.TextInput(attrs={"placeholder": "Ej.: Arriendo"}),
            "fecha": _campo_fecha(),
        }


class MetaForm(forms.ModelForm):
    class Meta:
        model = MetaAhorro
        fields = ["nombre", "objetivo", "ahorrado", "principal"]
        labels = {
            "nombre": "Nombre de la meta",
            "objetivo": "Monto que quieres lograr (en pesos)",
            "ahorrado": "Lo que llevas ahorrado (en pesos)",
            "principal": "Marcar como mi meta principal",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"placeholder": "Ej.: Fondo de emergencia"}),
        }

    def clean_objetivo(self):
        objetivo = self.cleaned_data["objetivo"]
        if objetivo <= 0:
            raise ValidationError("El monto de la meta debe ser mayor que cero.")
        return objetivo

    def clean_ahorrado(self):
        ahorrado = self.cleaned_data["ahorrado"]
        if ahorrado < 0:
            raise ValidationError("Lo ahorrado no puede ser negativo.")
        return ahorrado

    def clean(self):
        datos = super().clean()
        objetivo = datos.get("objetivo")
        ahorrado = datos.get("ahorrado")
        if objetivo and ahorrado is not None and ahorrado > objetivo:
            self.add_error("ahorrado", "Lo ahorrado no puede superar el monto de la meta.")
        return datos


class RecordatorioForm(MontoPositivoMixin, forms.ModelForm):
    class Meta:
        model = Recordatorio
        fields = ["nombre", "monto", "fecha"]
        labels = {
            "nombre": "¿Qué vas a pagar?",
            "monto": "Monto (en pesos)",
            "fecha": "Fecha de pago",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"placeholder": "Ej.: Arriendo"}),
            "fecha": _campo_fecha(),
        }

    def clean_fecha(self):
        fecha = self.cleaned_data["fecha"]
        # Una fecha pasada solo se acepta si no cambió al editar.
        if self.instance.pk and fecha == self.instance.fecha:
            return fecha
        if fecha < timezone.localdate():
            raise ValidationError("La fecha de pago no puede estar en el pasado.")
        return fecha


class AccesoForm(AuthenticationForm):
    """Inicio de sesión con correo (o usuario, para la cuenta de administrador)."""

    username = forms.CharField(
        label="Correo electrónico o usuario",
        widget=forms.TextInput(attrs={"autofocus": True}),
    )
    error_messages = {
        "invalid_login": "El correo o la contraseña no son correctos, o la cuenta está desactivada.",
        "inactive": "Esta cuenta está desactivada. Comunícate con el administrador.",
    }

    def clean_username(self):
        valor = self.cleaned_data["username"].strip()
        return valor.lower() if "@" in valor else valor


class RegistroForm(forms.Form):
    nombre = forms.CharField(label="Nombre", max_length=50)
    correo = forms.EmailField(label="Correo electrónico")
    clave = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput,
        help_text="Mínimo 8 caracteres. No uses solo números.",
    )
    clave2 = forms.CharField(
        label="Confirma tu contraseña",
        strip=False,
        widget=forms.PasswordInput,
    )
    privacidad = forms.BooleanField(
        label="Acepto el aviso de privacidad y el tratamiento de mis datos personales (Ley 1581 de 2012).",
        error_messages={"required": "Debes aceptar el aviso de privacidad para crear tu cuenta."},
    )

    def clean_correo(self):
        correo = self.cleaned_data["correo"].strip().lower()
        if Usuario.objects.filter(username__iexact=correo).exists():
            raise ValidationError("Ya existe una cuenta con este correo.")
        return correo

    def clean(self):
        datos = super().clean()
        clave = datos.get("clave")
        clave2 = datos.get("clave2")
        if clave and clave2 and clave != clave2:
            self.add_error("clave2", "Las contraseñas no coinciden.")
        elif clave:
            try:
                password_validation.validate_password(clave)
            except ValidationError as error:
                self.add_error("clave", error)
        return datos

    def guardar(self):
        datos = self.cleaned_data
        return Usuario.objects.create_user(
            username=datos["correo"],
            email=datos["correo"],
            password=datos["clave"],
            first_name=datos["nombre"],
        )
