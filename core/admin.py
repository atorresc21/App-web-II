from django.contrib import admin

from .models import Gasto, Ingreso, Meta, Recordatorio

admin.site.register(Ingreso)
admin.site.register(Gasto)
admin.site.register(Meta)
admin.site.register(Recordatorio)