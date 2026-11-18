from src.application.usecases.auth.login import LoginUseCase
from src.application.usecases.auth.registro import RegistroUseCase
from src.application.usecases.lineas.actualizar import ActualizarLineaUseCase
from src.application.usecases.lineas.crear import CrearLineaUseCase
from src.application.usecases.lineas.eliminar import EliminarLineaUseCase
from src.application.usecases.lineas.listar import ListarLineasUseCase
from src.application.usecases.lineas.obtener import ObtenerLineaUseCase
from src.application.usecases.puntos_control.listar import ListarPuntosControlUseCase
from src.application.usecases.usuarios.actualizar_rol import ActualizarRolUseCase
from src.application.usecases.usuarios.eliminar import EliminarUsuarioUseCase
from src.application.usecases.usuarios.listar import ListarUsuariosUseCase
from src.domain.repositories.linea_repository import LineaRepository
from src.domain.repositories.punto_control_repository import PuntoControlRepository
from src.domain.repositories.solicitud_registro_repository import SolicitudRegistroRepository
from src.domain.repositories.unidad_repository import UnidadRepository
from src.domain.repositories.usuario_repository import UsuarioRepository
from src.infrastructure.repositories.django_linea_repository import DjangoLineaRepository
from src.infrastructure.repositories.django_punto_control_repository import (
    DjangoPuntoControlRepository,
)
from src.infrastructure.repositories.django_solicitud_registro_repository import (
    DjangoSolicitudRegistroRepository,
)
from src.infrastructure.repositories.django_unidad_repository import DjangoUnidadRepository
from src.infrastructure.repositories.django_usuario_repository import DjangoUsuarioRepository


def usuario_repository() -> UsuarioRepository:
    return DjangoUsuarioRepository()


def solicitud_registro_repository() -> SolicitudRegistroRepository:
    return DjangoSolicitudRegistroRepository()


def login_use_case() -> LoginUseCase:
    return LoginUseCase(usuario_repository(), solicitud_registro_repository())


def registro_use_case() -> RegistroUseCase:
    return RegistroUseCase(
        usuario_repository(),
        solicitud_registro_repository(),
        linea_repository(),
    )


def listar_usuarios_use_case() -> ListarUsuariosUseCase:
    return ListarUsuariosUseCase(usuario_repository())


def actualizar_rol_use_case() -> ActualizarRolUseCase:
    return ActualizarRolUseCase(usuario_repository())


def eliminar_usuario_use_case() -> EliminarUsuarioUseCase:
    return EliminarUsuarioUseCase(usuario_repository())


def linea_repository() -> LineaRepository:
    return DjangoLineaRepository()


def unidad_repository() -> UnidadRepository:
    return DjangoUnidadRepository()


def punto_control_repository() -> PuntoControlRepository:
    return DjangoPuntoControlRepository()


def listar_lineas_use_case() -> ListarLineasUseCase:
    return ListarLineasUseCase(linea_repository())


def obtener_linea_use_case() -> ObtenerLineaUseCase:
    return ObtenerLineaUseCase(linea_repository())


def crear_linea_use_case() -> CrearLineaUseCase:
    return CrearLineaUseCase(linea_repository())


def actualizar_linea_use_case() -> ActualizarLineaUseCase:
    return ActualizarLineaUseCase(linea_repository())


def eliminar_linea_use_case() -> EliminarLineaUseCase:
    return EliminarLineaUseCase(linea_repository())


def listar_puntos_control_use_case() -> ListarPuntosControlUseCase:
    return ListarPuntosControlUseCase(linea_repository(), punto_control_repository())
