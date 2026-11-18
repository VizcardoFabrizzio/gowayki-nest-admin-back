from datetime import UTC, datetime

from src.application.dtos.linea import CrearLineaDTO
from src.domain.entities.linea import Linea
from src.domain.exceptions import ValidacionError
from src.domain.repositories.linea_repository import LineaRepository
from src.domain.value_objects import ColorHex


class CrearLineaUseCase:
    def __init__(self, repositorio: LineaRepository) -> None:
        self._repositorio = repositorio

    def ejecutar(self, datos: CrearLineaDTO) -> Linea:
        nombre = (datos.nombre or "").strip()
        if not nombre:
            raise ValidacionError("El nombre de la línea es obligatorio.")

        linea = Linea(
            id=None,
            nombre=nombre,
            origen=(datos.origen or "").strip(),
            destino=(datos.destino or "").strip(),
            corredor=self._texto_opcional(datos.corredor),
            color_hex=str(ColorHex(datos.color_hex or "#E53E3E")),
            created_at=datetime.now(UTC),
        )
        return self._repositorio.save(linea)

    @staticmethod
    def _texto_opcional(valor: str | None) -> str | None:
        texto = (valor or "").strip()
        return texto or None
