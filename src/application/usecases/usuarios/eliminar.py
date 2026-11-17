from uuid import UUID

from src.domain.exceptions import ConflictoError, NoEncontradoError
from src.domain.repositories.usuario_repository import UsuarioRepository
from src.domain.value_objects import Rol


class EliminarUsuarioUseCase:
    def __init__(self, repositorio: UsuarioRepository) -> None:
        self._repositorio = repositorio

    def ejecutar(self, usuario_id: UUID) -> None:
        usuario = self._repositorio.find_by_id(usuario_id)
        if usuario is None:
            raise NoEncontradoError("El usuario no existe.")
        if usuario.rol == Rol.ADMIN and self._repositorio.count_admins() <= 1:
            raise ConflictoError("No se puede eliminar al último administrador.")
        self._repositorio.delete(usuario_id)
