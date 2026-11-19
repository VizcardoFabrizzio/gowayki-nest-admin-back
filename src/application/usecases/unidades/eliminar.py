from src.domain.exceptions import ConflictoError, NoEncontradoError
from src.domain.repositories.unidad_repository import UnidadRepository


class EliminarUnidadUseCase:
    def __init__(self, repositorio: UnidadRepository) -> None:
        self._repositorio = repositorio

    def ejecutar(self, unidad_id: int) -> None:
        if not self._repositorio.exists_by_id(unidad_id):
            raise NoEncontradoError("La unidad no existe.")
        if self._repositorio.has_registros(unidad_id):
            raise ConflictoError(
                "No se puede eliminar la unidad porque tiene turnos o alertas asociadas."
            )
        self._repositorio.delete(unidad_id)
