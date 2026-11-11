from django.db import models

from src.infrastructure.models.linea import Linea


class Unidad(models.Model):
    id = models.AutoField(primary_key=True)
    numero_padron = models.CharField(max_length=10)
    placa = models.CharField(max_length=10, unique=True)
    linea = models.ForeignKey(
        Linea,
        on_delete=models.RESTRICT,
        db_column="linea_id",
        related_name="unidades",
    )
    estado = models.CharField(max_length=20, default="OPERATIVA")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        app_label = "core"
        db_table = "unidad"
