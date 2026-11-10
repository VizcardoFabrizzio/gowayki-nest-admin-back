from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PuntoControl:
    id: int
    linea_id: int
    nombre: str
    orden: int
    lat: float
    lng: float
    radio_tolerancia_metros: int
    tolerancia_minutos: int
    created_at: datetime
