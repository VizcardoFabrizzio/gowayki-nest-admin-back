from django.db import models


class Linea(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    corredor = models.CharField(max_length=50, null=True, blank=True)
    color_hex = models.CharField(max_length=7, default="#E53E3E")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        app_label = "core"
        db_table = "linea"
