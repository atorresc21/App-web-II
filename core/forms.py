
from django import forms
from django.utils import timezone
from .models import Ingreso, Gasto, Meta, Recordatorio


class IngresoForm(forms.ModelForm):
    class Meta:
        model = Ingreso
        fields = ["descripcion", "monto", "fecha", "periodicidad"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"})
        }

    def clean_monto(self):
        monto = self.cleaned_data.get("monto")
        if monto is not None and monto <= 0:
            raise forms.ValidationError("El monto debe ser mayor que cero.")
        return monto

    def clean_fecha(self):
        fecha = self.cleaned_data.get("fecha")
        if fecha and fecha > timezone.localdate():
            raise forms.ValidationError("La fecha no puede ser futura.")
        return fecha


class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = ["descripcion", "monto", "fecha", "categoria", "tipo"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"})
        }

    def clean_monto(self):
        monto = self.cleaned_data.get("monto")
        if monto is not None and monto < 0:
            raise forms.ValidationError("El monto no puede ser negativo.")
        return monto


class MetaForm(forms.ModelForm):
    class Meta:
        model = Meta
        fields = ["nombre", "objetivo", "ahorrado", "principal"]

    def clean_objetivo(self):
        objetivo = self.cleaned_data.get("objetivo")
        if objetivo is not None and objetivo <= 0:
            raise forms.ValidationError("El objetivo debe ser mayor que cero.")
        return objetivo

    def clean(self):
        cleaned_data = super().clean()
        objetivo = cleaned_data.get("objetivo")
        ahorrado = cleaned_data.get("ahorrado")

        if objetivo is not None and ahorrado is not None and ahorrado > objetivo:
            self.add_error("ahorrado", "El ahorro no puede superar el objetivo.")

        return cleaned_data


class RecordatorioForm(forms.ModelForm):
    class Meta:
        model = Recordatorio
        fields = ["nombre", "monto", "fecha"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"})
        }

    def clean_monto(self):
        monto = self.cleaned_data.get("monto")
        if monto is not None and monto <= 0:
            raise forms.ValidationError("El monto debe ser mayor que cero.")
        return monto

    def clean_fecha(self):
        fecha = self.cleaned_data.get("fecha")
        if fecha and fecha < timezone.localdate():
            raise forms.ValidationError("La fecha no puede estar en el pasado.")
        return fecha
