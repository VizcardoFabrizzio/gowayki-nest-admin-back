from django.db import models


class UsuarioLinea(models.Model):
    usuario_id = models.UUIDField(primary_key=True)
    linea_id = models.IntegerField()
    subruta_id = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        app_label = "core"
        db_table = "usuario_linea"
