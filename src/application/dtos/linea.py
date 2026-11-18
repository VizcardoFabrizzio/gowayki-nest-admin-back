from dataclasses import dataclass


@dataclass(frozen=True)
class CrearLineaDTO:
    nombre: str
    origen: str = ""
    destino: str = ""
    corredor: str | None = None
    color_hex: str = "#E53E3E"


@dataclass(frozen=True)
class ActualizarLineaDTO:
    nombre: str | None = None
    origen: str | None = None
    destino: str | None = None
    corredor: str | None = None
    color_hex: str | None = None
