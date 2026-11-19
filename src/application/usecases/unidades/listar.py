from src.domain.entities.unidad import Unidad
from src.domain.repositories.unidad_repository import UnidadRepository


class ListarUnidadesUseCase:
    def __init__(self, repositorio: UnidadRepository) -> None:
        self._repositorio = repositorio

    def ejecutar(self) -> list[Unidad]:
        return self._repositorio.find_all()
