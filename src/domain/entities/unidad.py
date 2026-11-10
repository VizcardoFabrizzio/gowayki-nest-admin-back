from dataclasses import dataclass
from datetime import datetime

from src.domain.value_objects import EstadoUnidad


@dataclass(frozen=True)
class Unidad:
    id: int
    numero_padron: str
    placa: str
    linea_id: int
    estado: EstadoUnidad
    created_at: datetime
