from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.value_objects import EstadoSolicitud, TipoSolicitud


@dataclass(frozen=True)
class SolicitudRegistro:
    id: int | None
    tipo: TipoSolicitud
    dni: str
    nombre_completo: str
    estado: EstadoSolicitud
    creado_en: datetime
    telefono: str | None = None
    email: str | None = None
    ruta_trabajo: str | None = None
    placa_numero: str | None = None
    linea_solicitada_id: int | None = None
    subruta_solicitada_id: int | None = None
    usuario_id: UUID | None = None
    pin_hash: str | None = None
    usuario_asignado: str | None = None
    actualizado_en: datetime | None = None
