from dataclasses import dataclass
from datetime import datetime

from src.domain.value_objects import EstadoSolicitud, TipoSolicitud


@dataclass(frozen=True)
class SolicitudRegistro:
    id: int | None
    tipo: TipoSolicitud
    dni: str
    nombre_completo: str
    telefono: str | None
    email: str | None
    ruta_trabajo: str | None
    linea_solicitada_id: int | None
    pin_hash: str | None
    estado: EstadoSolicitud
    creado_en: datetime
