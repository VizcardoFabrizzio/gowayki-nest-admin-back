import datetime

import jwt
from django.conf import settings
from rest_framework import authentication, exceptions

from src.domain.entities.usuario import Usuario
from src.infrastructure.repositories.django_usuario_repository import (
    DjangoUsuarioRepository,
)


def _usuario_repository():
    return DjangoUsuarioRepository()


def _secret() -> str:
    return settings.SECRET_KEY


def generar_token(usuario: Usuario) -> str:
    """Genera un token JWT firmado con los datos del usuario."""
    ahora = datetime.datetime.now(datetime.UTC)
    payload = {
        "user_id": str(usuario.id),
        "rol": usuario.rol.value,
        "linea_id": usuario.linea_id,
        "linea_nombre": usuario.linea_nombre,
        "iat": ahora,
        "exp": ahora + datetime.timedelta(hours=24),
    }
    return jwt.encode(payload, _secret(), algorithm="HS256")


class UsuarioAutenticado:
    """Envoltura del Usuario del dominio para DRF (is_authenticated)."""

    is_authenticated = True

    def __init__(self, usuario):
        self.usuario = usuario
        for attr in (
            "id",
            "nombre",
            "dni",
            "telefono",
            "email",
            "foto_url",
            "rol",
            "is_online",
            "linea_id",
            "linea_nombre",
        ):
            setattr(self, attr, getattr(usuario, attr))


class AutenticacionJWT(authentication.BaseAuthentication):
    """Autenticacion basada en JWT para el panel de administracion."""

    def authenticate(self, request):
        header = request.META.get("HTTP_AUTHORIZATION", "")
        if not header.startswith("Bearer "):
            return None

        token_str = header[len("Bearer ") :].strip()
        if not token_str:
            return None

        try:
            payload = jwt.decode(token_str, _secret(), algorithms=["HS256"])
        except jwt.ExpiredSignatureError as exc:
            raise exceptions.AuthenticationFailed("Token expirado.") from exc
        except jwt.InvalidTokenError as exc:
            raise exceptions.AuthenticationFailed("Token invalido.") from exc

        user_id = payload.get("user_id")
        if not user_id:
            raise exceptions.AuthenticationFailed("Token invalido.")

        from uuid import UUID as _UUID

        try:
            user_uuid = _UUID(str(user_id))
        except (ValueError, AttributeError) as exc:
            raise exceptions.AuthenticationFailed("Token invalido.") from exc

        usuario = _usuario_repository().find_by_id(user_uuid)
        if usuario is None:
            raise exceptions.AuthenticationFailed("Usuario no encontrado.")

        return (UsuarioAutenticado(usuario), payload)

    def authenticate_header(self, request):
        return 'Bearer realm="gowayki-admin"'
