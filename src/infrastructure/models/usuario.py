import uuid

from django.db import models


class Usuario(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    nombre = models.CharField(max_length=100)
    dni = models.CharField(max_length=8, unique=True)
    telefono = models.CharField(max_length=9, unique=True)
    email = models.CharField(max_length=120, unique=True, null=True, blank=True)
    pin_hash = models.CharField(max_length=255)
    foto_url = models.CharField(max_length=255, null=True, blank=True)
    rol = models.CharField(max_length=20, default="CHOFER")
    is_online = models.BooleanField(default=False)
    intentos_fallidos = models.IntegerField(default=0)
    bloqueado_hasta = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        app_label = "core"
        db_table = "usuario"
