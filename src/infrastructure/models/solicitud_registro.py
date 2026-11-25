from django.db import models


class SolicitudRegistro(models.Model):
    id = models.BigAutoField(primary_key=True)
    tipo = models.CharField(max_length=20, default="JEFE_RUTA")
    dni = models.CharField(max_length=8)
    nombre_completo = models.CharField(max_length=100)
    telefono = models.CharField(max_length=9, null=True, blank=True)
    email = models.CharField(max_length=120, null=True, blank=True)
    placa_numero = models.CharField(max_length=10, null=True, blank=True)
    ruta_trabajo = models.CharField(max_length=100, null=True, blank=True)
    usuario_id = models.UUIDField(null=True, blank=True)
    linea_solicitada_id = models.IntegerField(null=True, blank=True)
    subruta_solicitada_id = models.IntegerField(null=True, blank=True)
    pin_hash = models.CharField(max_length=255, null=True, blank=True)
    estado = models.CharField(max_length=20, default="PENDIENTE")
    usuario_asignado = models.CharField(max_length=50, null=True, blank=True)
    creado_en = models.DateTimeField()
    actualizado_en = models.DateTimeField()

    class Meta:
        managed = False
        app_label = "core"
        db_table = "solicitud_registro"
