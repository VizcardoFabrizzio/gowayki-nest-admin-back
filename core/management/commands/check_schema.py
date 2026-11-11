from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from src.infrastructure.models.linea import Linea
from src.infrastructure.models.punto_control import PuntoControl
from src.infrastructure.models.unidad import Unidad
from src.infrastructure.models.usuario import Usuario

MODELOS = {
    "usuario": Usuario,
    "linea": Linea,
    "unidad": Unidad,
    "punto_control": PuntoControl,
}

IGNORADAS = {
    "punto_control": {"ubicacion"},
}


class Command(BaseCommand):
    help = "Verifica que los modelos coincidan con las tablas existentes."

    def handle(self, *args, **options):
        diferencias = []

        with connection.cursor() as cursor:
            for tabla, modelo in MODELOS.items():
                try:
                    columnas_db = {
                        columna.name
                        for columna in connection.introspection.get_table_description(
                            cursor, tabla
                        )
                    }
                except Exception as exc:
                    raise CommandError(f"No se pudo leer la tabla {tabla}: {exc}") from exc

                columnas_db -= IGNORADAS.get(tabla, set())
                columnas_modelo = {campo.column for campo in modelo._meta.local_fields}

                faltantes = columnas_db - columnas_modelo
                sobrantes = columnas_modelo - columnas_db

                if faltantes or sobrantes:
                    diferencias.append((tabla, faltantes, sobrantes))
                    self.stderr.write(f"{tabla}:")
                    if faltantes:
                        self.stderr.write(
                            f"  faltan en el modelo: {', '.join(sorted(faltantes))}"
                        )
                    if sobrantes:
                        self.stderr.write(
                            f"  sobran en el modelo: {', '.join(sorted(sobrantes))}"
                        )
                else:
                    self.stdout.write(f"{tabla}: ok")

        if diferencias:
            raise CommandError("El esquema no coincide con los modelos.")

        self.stdout.write(self.style.SUCCESS("Esquema verificado."))
