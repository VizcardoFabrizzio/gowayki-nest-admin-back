from dataclasses import replace
from datetime import UTC, datetime, timedelta

from src.domain.entities.usuario import Usuario
from src.domain.exceptions import (
    AccesoDenegadoError,
    CredencialesInvalidasError,
    CuentaBloqueadaError,
    ValidacionError,
)
from src.domain.repositories.usuario_repository import CredencialesUsuario, UsuarioRepository
from src.domain.value_objects import Dni, Pin, Rol
from src.infrastructure.security.pin_hasher import PinHasher

MAX_INTENTOS = 5
MINUTOS_BLOQUEO = 15


class LoginUseCase:
    def __init__(self, repositorio: UsuarioRepository) -> None:
        self._repositorio = repositorio

    def ejecutar(self, identificador: str, pin: str) -> Usuario:
        identificador = (identificador or "").strip()
        if not identificador:
            raise ValidacionError("El DNI es obligatorio.")
        if not pin or not pin.strip():
            raise ValidacionError("El PIN es obligatorio.")
        Pin(pin)

        credenciales = self._buscar(identificador)
        if credenciales is None:
            raise CredencialesInvalidasError("Credenciales inválidas.")

        ahora = datetime.now(UTC)
        if credenciales.bloqueado_hasta and credenciales.bloqueado_hasta > ahora:
            raise CuentaBloqueadaError(
                "Cuenta bloqueada temporalmente. Intenta de nuevo más tarde."
            )

        intentos = credenciales.intentos_fallidos
        if credenciales.bloqueado_hasta is not None:
            intentos = 0

        if not PinHasher.verify(pin, credenciales.pin_hash):
            intentos += 1
            if intentos >= MAX_INTENTOS:
                self._repositorio.update_login_state(
                    credenciales.id,
                    False,
                    MAX_INTENTOS,
                    ahora + timedelta(minutes=MINUTOS_BLOQUEO),
                )
                raise CuentaBloqueadaError(
                    "Cuenta bloqueada temporalmente. Intenta de nuevo en 15 minutos."
                )
            self._repositorio.update_login_state(credenciales.id, False, intentos, None)
            raise CredencialesInvalidasError(
                f"PIN incorrecto. Intentos restantes: {MAX_INTENTOS - intentos}"
            )

        usuario = self._repositorio.find_by_id(credenciales.id)
        if usuario is None:
            raise CredencialesInvalidasError("Credenciales inválidas.")
        if usuario.rol != Rol.ADMIN:
            raise AccesoDenegadoError("Esta cuenta no tiene acceso al panel.")

        self._repositorio.update_login_state(credenciales.id, True, 0, None)
        return replace(usuario, is_online=True)

    def _buscar(self, identificador: str) -> CredencialesUsuario | None:
        if "@" in identificador:
            return self._repositorio.find_auth_by_email(identificador)
        Dni(identificador)
        return self._repositorio.find_auth_by_dni(identificador)
