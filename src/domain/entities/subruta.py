from dataclasses import dataclass


@dataclass(frozen=True)
class Subruta:
    """Subruta de una línea, compartida con la API Java (solo lectura)."""

    id: int
    codigo: str
    nombre: str
    linea_codigo: str | None
    activa: bool = True
