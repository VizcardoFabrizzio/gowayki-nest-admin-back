from dataclasses import replace
from uuid import UUID

from src.application.dtos.usuario import ActualizarRolDTO
from src.domain.entities.usuario import Usuario
from src.domain.exceptions import ConflictoError, NoEncontradoError, ValidacionError
from src.domain.repositories.usuario_repository import UsuarioRepository
from src.domain.value_objects import Rol

ROLES_PERMITIDOS = (Rol.ADMIN.value, Rol.JEFE_RUTA.value)


class ActualizarRolUseCase:
    def __init__(self, repositorio: UsuarioRepository) -> None:
        self._repositorio = repositorio

    def ejecutar(self, usuario_id: UUID, datos: ActualizarRolDTO) -> Usuario:
        rol = (datos.rol or "").strip().upper()
        if rol not in ROLES_PERMITIDOS:
            raise ValidacionError("El rol debe ser ADMIN o JEFE_RUTA.")

        usuario = self._repositorio.find_by_id(usuario_id)
        if usuario is None:
            raise NoEncontradoError("El usuario no existe.")
        if usuario.rol == Rol.CHOFER:
            raise ValidacionError("Las cuentas de chofer no se cambian desde el panel.")
        if (
            usuario.rol == Rol.ADMIN
            and rol != Rol.ADMIN.value
            and self._repositorio.count_admins() <= 1
        ):
            raise ConflictoError("No se puede quitar el último administrador.")

        actualizado = replace(usuario, rol=Rol(rol))
        return self._repositorio.save(actualizado)
