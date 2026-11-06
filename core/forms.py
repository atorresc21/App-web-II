from django import forms
from .models import Ingreso, Gasto, Meta, Recordatorio




class IngresoForm(forms.ModelForm):
    class Meta:
        model = Ingreso
        fields = ["descripcion", "monto", "fecha", "periodicidad"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"})
        }




class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = ["descripcion", "monto", "fecha", "categoria", "tipo"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"})
        }




class MetaForm(forms.ModelForm):
    class Meta:
        model = Meta
        fields = ["nombre", "objetivo", "ahorrado", "principal"]




class RecordatorioForm(forms.ModelForm):
    class Meta:
        model = Recordatorio
        fields = ["nombre", "monto", "fecha"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"})
        }