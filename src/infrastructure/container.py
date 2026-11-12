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


def linea_repository() -> LineaRepository:
    return DjangoLineaRepository()


def unidad_repository() -> UnidadRepository:
    return DjangoUnidadRepository()


def punto_control_repository() -> PuntoControlRepository:
    return DjangoPuntoControlRepository()
