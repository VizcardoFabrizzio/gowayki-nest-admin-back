import re
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from src.domain.exceptions import ValidacionError


class Rol(StrEnum):
    CHOFER = "CHOFER"
    ADMIN = "ADMIN"
    JEFE_RUTA = "JEFE_RUTA"


ESTADOS_UNIDAD_ALIAS = {
    "ACTIVA": "OPERATIVA",
    "ACTIVO": "OPERATIVA",
    "OPERATIVO": "OPERATIVA",
    "EN MANTENIMIENTO": "MANTENIMIENTO",
    "MANTENIMIENTO": "MANTENIMIENTO",
    "INACTIVA": "BAJA",
    "INACTIVO": "BAJA",
    "DE BAJA": "BAJA",
    "BAJA": "BAJA",
}


class EstadoUnidad(StrEnum):
    OPERATIVA = "OPERATIVA"
    MANTENIMIENTO = "MANTENIMIENTO"
    BAJA = "BAJA"

    @classmethod
    def del_panel(cls, valor: str) -> "EstadoUnidad":
        texto = " ".join((valor or "").strip().upper().split())
        alias = ESTADOS_UNIDAD_ALIAS.get(texto, texto)
        try:
            return cls(alias)
        except ValueError as exc:
            raise ValidacionError("El estado debe ser OPERATIVA, MANTENIMIENTO o BAJA.") from exc


class TipoSolicitud(StrEnum):
    JEFE_RUTA = "JEFE_RUTA"
    CHOFER = "CHOFER"
    CAMBIO_RUTA = "CAMBIO_RUTA"


class EstadoSolicitud(StrEnum):
    PENDIENTE = "PENDIENTE"
    APROBADA = "APROBADA"
    RECHAZADA = "RECHAZADA"


@dataclass(frozen=True)
class Dni:
    valor: str

    def __post_init__(self) -> None:
        valor = self.valor.strip()
        if len(valor) != 8 or not valor.isdigit():
            raise ValidacionError("El DNI debe tener exactamente 8 dígitos.")
        object.__setattr__(self, "valor", valor)

    def __str__(self) -> str:
        return self.valor


@dataclass(frozen=True)
class Telefono:
    valor: str

    def __post_init__(self) -> None:
        valor = self.valor.strip()
        if len(valor) != 9 or not valor.isdigit():
            raise ValidacionError("El teléfono debe tener exactamente 9 dígitos.")
        object.__setattr__(self, "valor", valor)

    def __str__(self) -> str:
        return self.valor


@dataclass(frozen=True)
class Pin:
    valor: str

    def __post_init__(self) -> None:
        valor = self.valor.strip()
        if len(valor) < 4 or not valor.isdigit():
            raise ValidacionError("El PIN debe tener al menos 4 dígitos numéricos.")
        object.__setattr__(self, "valor", valor)

    def __str__(self) -> str:
        return self.valor


@dataclass(frozen=True)
class ColorHex:
    valor: str

    def __post_init__(self) -> None:
        valor = self.valor.strip()
        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", valor):
            raise ValidacionError("El color debe tener el formato #RRGGBB.")
        object.__setattr__(self, "valor", valor)

    def __str__(self) -> str:
        return self.valor


@dataclass(frozen=True)
class PosicionGps:
    lat: float
    lng: float
    velocidad_kmh: float
    rumbo_grados: int
    ultima_actualizacion: datetime
