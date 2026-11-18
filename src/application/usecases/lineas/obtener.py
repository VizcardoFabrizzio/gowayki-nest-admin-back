from src.domain.entities.linea import Linea
from src.domain.exceptions import NoEncontradoError
from src.domain.repositories.linea_repository import LineaRepository


class ObtenerLineaUseCase:
    def __init__(self, repositorio: LineaRepository) -> None:
        self._repositorio = repositorio

    def ejecutar(self, linea_id: int) -> Linea:
        linea = self._repositorio.find_by_id(linea_id)
        if linea is None:
            raise NoEncontradoError("La línea no existe.")
        return linea
