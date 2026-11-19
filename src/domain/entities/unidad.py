from dataclasses import dataclass
from datetime import datetime

from src.domain.value_objects import EstadoUnidad, PosicionGps


@dataclass(frozen=True)
class Unidad:
    id: int | None
    numero_padron: str
    placa: str
    linea_id: int
    estado: EstadoUnidad
    created_at: datetime
    linea_nombre: str | None = None
    posicion_actual: PosicionGps | None = None
