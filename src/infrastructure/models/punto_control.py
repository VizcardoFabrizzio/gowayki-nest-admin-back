from django.db import models

from src.infrastructure.models.linea import Linea


class PuntoControl(models.Model):
    id = models.AutoField(primary_key=True)
    linea = models.ForeignKey(
        Linea,
        on_delete=models.CASCADE,
        db_column="linea_id",
        related_name="puntos_control",
    )
    nombre = models.CharField(max_length=100)
    orden = models.IntegerField()
    radio_tolerancia_metros = models.IntegerField(default=50)
    tolerancia_minutos = models.IntegerField(default=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        app_label = "core"
        db_table = "punto_control"
