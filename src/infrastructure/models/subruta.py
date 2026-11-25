from django.db import models


class Subruta(models.Model):
    """Solo lectura: tabla compartida con gowayki_db (Spring)."""

    id = models.IntegerField(primary_key=True)
    codigo = models.CharField(max_length=50)
    nombre = models.CharField(max_length=255)
    linea_codigo = models.CharField(max_length=20, null=True, blank=True)
    linea_nombre = models.CharField(max_length=100, null=True, blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        managed = False
        app_label = "core"
        db_table = "subruta"
