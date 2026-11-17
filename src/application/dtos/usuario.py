from dataclasses import dataclass


@dataclass(frozen=True)
class ActualizarRolDTO:
    rol: str
