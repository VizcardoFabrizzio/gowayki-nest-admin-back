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
    linea_id: int | None = None
    linea_nombre: str | None = None
    subruta_id: int | None = None
    subruta_nombre: str | None = None
    activo: bool = True
    token_version: int = 0
    eliminado_en: datetime | None = None
    reactivado_en: datetime | None = None
