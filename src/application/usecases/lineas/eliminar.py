from src.domain.exceptions import ConflictoError, NoEncontradoError
from src.domain.repositories.linea_repository import LineaRepository


class EliminarLineaUseCase:
    def __init__(self, repositorio: LineaRepository) -> None:
        self._repositorio = repositorio

    def ejecutar(self, linea_id: int) -> None:
        if not self._repositorio.exists_by_id(linea_id):
            raise NoEncontradoError("La línea no existe.")
        if self._repositorio.has_unidades(linea_id):
            raise ConflictoError("No se puede eliminar la línea porque tiene unidades asignadas.")
        self._repositorio.delete(linea_id)
