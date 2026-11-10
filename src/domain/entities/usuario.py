from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.value_objects import Rol


@dataclass(frozen=True)
class Usuario:
    id: UUID
    nombre: str
    dni: str
    telefono: str
    email: str | None
    foto_url: str | None
    rol: Rol
    is_online: bool
    created_at: datetime
