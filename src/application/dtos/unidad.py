from dataclasses import dataclass


@dataclass(frozen=True)
class CrearUnidadDTO:
    numero_padron: str = ""
    placa: str = ""
    linea_id: int | None = None
    estado: str = "OPERATIVA"
    subruta_id: int | None = None


@dataclass(frozen=True)
class ActualizarUnidadDTO:
    numero_padron: str | None = None
    placa: str | None = None
    linea_id: int | None = None
    estado: str | None = None
    subruta_id: int | None = None
    subruta_id_presente: bool = False


@dataclass(frozen=True)
class ListarUnidadesPorLineaDTO:
    linea_id: int
