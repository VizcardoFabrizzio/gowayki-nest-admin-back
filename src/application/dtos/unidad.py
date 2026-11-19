from dataclasses import dataclass


@dataclass(frozen=True)
class CrearUnidadDTO:
    numero_padron: str = ""
    placa: str = ""
    linea_id: int | None = None
    estado: str = "OPERATIVA"


@dataclass(frozen=True)
class ActualizarUnidadDTO:
    numero_padron: str | None = None
    placa: str | None = None
    linea_id: int | None = None
    estado: str | None = None


@dataclass(frozen=True)
class ListarUnidadesPorLineaDTO:
    linea_id: int
