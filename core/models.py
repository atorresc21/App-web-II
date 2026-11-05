from django.conf import settings
from django.db import models


class Ingreso(models.Model):
    PERIODICIDADES = [
        ("diaria", "Diaria"),
        ("semanal", "Semanal"),
        ("quincenal", "Quincenal"),
        ("mensual", "Mensual"),
        ("variable", "Variable"),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ingresos")
    descripcion = models.CharField(max_length=100)
    monto = models.DecimalField(max_digits=12, decimal_places=0)
    fecha = models.DateField()
    periodicidad = models.CharField(max_length=10, choices=PERIODICIDADES, default="quincenal")

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.descripcion} - {self.monto}"


class Gasto(models.Model):
    CATEGORIAS = [
        ("vivienda", "Vivienda"),
        ("alimentacion", "Alimentación"),
        ("transporte", "Transporte"),
        ("servicios", "Servicios"),
        ("salud", "Salud"),
        ("educacion", "Educación"),
        ("ocio", "Ocio"),
        ("otros", "Otros"),
    ]
    TIPOS = [("fijo", "Fijo"), ("variable", "Variable")]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="gastos")
    descripcion = models.CharField(max_length=100)
    monto = models.DecimalField(max_digits=12, decimal_places=0)
    fecha = models.DateField()
    categoria = models.CharField(max_length=15, choices=CATEGORIAS, default="otros")
    tipo = models.CharField(max_length=10, choices=TIPOS, default="variable")

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.descripcion} - {self.monto}"


class Meta(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="metas")
    nombre = models.CharField(max_length=100)
    objetivo = models.DecimalField(max_digits=12, decimal_places=0)
    ahorrado = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    principal = models.BooleanField(default=False)

    def avance(self):
        if self.objetivo:
            return min(100, int(self.ahorrado * 100 / self.objetivo))
        return 0

    def save(self, *args, **kwargs):
        # Solo puede haber una meta principal por usuario.
        super().save(*args, **kwargs)
        if self.principal:
            Meta.objects.filter(usuario=self.usuario).exclude(pk=self.pk).update(principal=False)

    def __str__(self):
        return self.nombre


class Recordatorio(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recordatorios")
    nombre = models.CharField(max_length=100)
    monto = models.DecimalField(max_digits=12, decimal_places=0)
    fecha = models.DateField()

    class Meta:
        ordering = ["fecha"]

    def __str__(self):
        return self.nombre