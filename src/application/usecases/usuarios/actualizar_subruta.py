from uuid import UUID

from src.application.dtos.usuario import ActualizarSubrutaDTO
from src.domain.entities.usuario import Usuario
from src.domain.exceptions import NoEncontradoError, ValidacionError
from src.domain.repositories.usuario_repository import UsuarioRepository
from src.domain.value_objects import Rol


class ActualizarSubrutaUseCase:
    """Cambia la subruta asignada a un JEFE_RUTA desde el panel."""

    def __init__(self, repositorio: UsuarioRepository) -> None:
        self._repositorio = repositorio

    def ejecutar(self, usuario_id: UUID, datos: ActualizarSubrutaDTO) -> Usuario:
        if datos.subruta_id is None or datos.subruta_id <= 0:
            raise ValidacionError("Debes seleccionar una subruta válida.")

        usuario = self._repositorio.find_by_id(usuario_id)
        if usuario is None:
            raise NoEncontradoError("El usuario no existe.")
        if usuario.rol != Rol.JEFE_RUTA:
            raise ValidacionError("Solo se puede asignar subruta a un jefe de ruta.")

        actualizado = self._repositorio.asignar_subruta(usuario_id, datos.subruta_id)
        if actualizado is None:
            raise ValidacionError("El jefe aún no tiene una línea asignada.")
        return actualizado
