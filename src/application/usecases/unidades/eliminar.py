from src.domain.exceptions import NoEncontradoError
from src.domain.repositories.unidad_repository import UnidadRepository


class EliminarUnidadUseCase:
    def __init__(self, repositorio: UnidadRepository) -> None:
        self._repositorio = repositorio

    def ejecutar(self, unidad_id: int) -> str:
        if not self._repositorio.exists_by_id(unidad_id):
            raise NoEncontradoError("La unidad no existe.")
        if self._repositorio.has_registros(unidad_id):
            # Borrado lógico: la unidad tiene historial, se desactiva en lugar
            # de borrar físicamente para no romper turnos ni alertas.
            self._repositorio.desactivar(unidad_id)
            return "desactivada"
        self._repositorio.delete(unidad_id)
        return "eliminada"
