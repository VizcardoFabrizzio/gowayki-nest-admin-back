from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from src.infrastructure.models.linea import Linea
from src.infrastructure.models.punto_control import PuntoControl
from src.infrastructure.models.solicitud_registro import SolicitudRegistro
from src.infrastructure.models.subruta import Subruta
from src.infrastructure.models.unidad import Unidad
from src.infrastructure.models.usuario import Usuario
from src.infrastructure.models.usuario_linea import UsuarioLinea

MODELOS = {
    "usuario": Usuario,
    "linea": Linea,
    "unidad": Unidad,
    "punto_control": PuntoControl,
    "usuario_linea": UsuarioLinea,
    "solicitud_registro": SolicitudRegistro,
    "subruta": Subruta,
}

IGNORADAS = {
    "punto_control": {"ubicacion"},
    # La API Java almacena la linea en usuario.linea_id; el esquema Django usa
    # la tabla usuario_linea. El campo es ajeno a este backend.
    "usuario": {"linea_id"},
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
                        for columna in connection.introspection.get_table_description(cursor, tabla)
                    }
                except Exception as exc:
                    raise CommandError(f"No se pudo leer la tabla {tabla}: {exc}") from exc

                columnas_db -= IGNORADAS.get(tabla, set())
                columnas_modelo = {campo.column for campo in modelo._meta.local_fields}

                # La BD es compartida con la API Java: puede tener columnas que
                # este backend no mapea (modelos unmanaged). Solo verificamos
                # que las columnas que SÍ usamos existan.
                sobrantes = columnas_modelo - columnas_db

                if sobrantes:
                    diferencias.append((tabla, sobrantes))
                    self.stderr.write(f"{tabla}:")
                    self.stderr.write(
                        f"  columnas del modelo ausentes en la BD: {', '.join(sorted(sobrantes))}"
                    )
                else:
                    self.stdout.write(f"{tabla}: ok")

        if diferencias:
            raise CommandError("El esquema no coincide con los modelos.")

        self.stdout.write(self.style.SUCCESS("Esquema verificado."))
