from dataclasses import dataclass


@dataclass(frozen=True)
class ListarPuntosControlDTO:
    linea_id: int
