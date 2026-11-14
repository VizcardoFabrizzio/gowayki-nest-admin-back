from src.application.usecases.auth.login import LoginUseCase
from src.application.usecases.auth.registro import RegistroUseCase
from src.domain.repositories.linea_repository import LineaRepository
from src.domain.repositories.punto_control_repository import PuntoControlRepository
from src.domain.repositories.unidad_repository import UnidadRepository
from src.domain.repositories.usuario_repository import UsuarioRepository
from src.infrastructure.repositories.django_linea_repository import DjangoLineaRepository
from src.infrastructure.repositories.django_punto_control_repository import (
    DjangoPuntoControlRepository,
)
from src.infrastructure.repositories.django_unidad_repository import DjangoUnidadRepository
from src.infrastructure.repositories.django_usuario_repository import DjangoUsuarioRepository


def usuario_repository() -> UsuarioRepository:
    return DjangoUsuarioRepository()


def login_use_case() -> LoginUseCase:
    return LoginUseCase(usuario_repository())


def registro_use_case() -> RegistroUseCase:
    return RegistroUseCase(usuario_repository())


def linea_repository() -> LineaRepository:
    return DjangoLineaRepository()


def unidad_repository() -> UnidadRepository:
    return DjangoUnidadRepository()


def punto_control_repository() -> PuntoControlRepository:
    return DjangoPuntoControlRepository()
