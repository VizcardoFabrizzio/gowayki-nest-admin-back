from src.domain.entities.linea import Linea
from src.domain.repositories.linea_repository import LineaRepository


class ListarLineasUseCase:
    def __init__(self, repositorio: LineaRepository) -> None:
        self._repositorio = repositorio

    def ejecutar(self) -> list[Linea]:
        return self._repositorio.find_all()
