from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Linea:
    id: int
    nombre: str
    origen: str
    destino: str
    corredor: str | None
    color_hex: str
    created_at: datetime
