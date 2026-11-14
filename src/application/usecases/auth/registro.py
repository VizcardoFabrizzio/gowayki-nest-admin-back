from datetime import UTC, datetime
from uuid import uuid4

from src.application.dtos.auth import RegistroDTO
from src.domain.entities.usuario import Usuario
from src.domain.exceptions import ConflictoError, ValidacionError
from src.domain.repositories.usuario_repository import UsuarioRepository
from src.domain.value_objects import Dni, Pin, Rol, Telefono
from src.infrastructure.security.pin_hasher import PinHasher


class RegistroUseCase:
    def __init__(self, repositorio: UsuarioRepository) -> None:
        self._repositorio = repositorio

    def ejecutar(self, datos: RegistroDTO) -> Usuario:
        nombre = (datos.nombre or "").strip()
        if not nombre:
            raise ValidacionError("El nombre es obligatorio.")

        dni = Dni(datos.dni or "")
        telefono = Telefono(datos.telefono or "")
        pin = Pin(datos.pin or "")
        email = self._normalizar_email(datos.email)

        if self._repositorio.exists_by_dni(str(dni)):
            raise ConflictoError("El DNI ya está registrado.")
        if self._repositorio.exists_by_telefono(str(telefono)):
            raise ConflictoError("El teléfono ya está registrado.")
        if email and self._repositorio.exists_by_email(email):
            raise ConflictoError("El email ya está registrado.")

        usuario = Usuario(
            id=uuid4(),
            nombre=nombre,
            dni=str(dni),
            telefono=str(telefono),
            email=email,
            foto_url=None,
            rol=Rol.ADMIN,
            is_online=False,
            created_at=datetime.now(UTC),
        )
        return self._repositorio.save(usuario, PinHasher.hash(str(pin)))

    @staticmethod
    def _normalizar_email(valor: str | None) -> str | None:
        email = (valor or "").strip().lower()
        if not email:
            return None
        dominio = email.split("@")[-1]
        if "@" not in email or "." not in dominio:
            raise ValidacionError("El email no es válido.")
        return email
