from dataclasses import dataclass


@dataclass(frozen=True)
class ActualizarRolDTO:
    rol: str


@dataclass(frozen=True)
class ActualizarSubrutaDTO:
    subruta_id: int
