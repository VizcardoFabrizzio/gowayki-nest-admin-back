from datetime import UTC, datetime
from uuid import uuid4

import pytest

import src.infrastructure.security.jwt as jwt_module
from src.application.usecases.auth.login import LoginUseCase
from src.application.usecases.auth.registro import RegistroUseCase
from src.application.usecases.lineas.actualizar import ActualizarLineaUseCase
from src.application.usecases.lineas.crear import CrearLineaUseCase
from src.application.usecases.lineas.eliminar import EliminarLineaUseCase
from src.application.usecases.lineas.listar import ListarLineasUseCase
from src.application.usecases.lineas.obtener import ObtenerLineaUseCase
from src.application.usecases.puntos_control.listar import ListarPuntosControlUseCase
from src.application.usecases.solicitudes.crear_cambio_ruta import CrearCambioRutaUseCase
from src.application.usecases.solicitudes.listar import ListarSolicitudesUseCase
from src.application.usecases.solicitudes.resolver import ResolverSolicitudUseCase
from src.application.usecases.unidades.actualizar import ActualizarUnidadUseCase
from src.application.usecases.unidades.crear import CrearUnidadUseCase
from src.application.usecases.unidades.eliminar import EliminarUnidadUseCase
from src.application.usecases.unidades.listar import ListarUnidadesUseCase
from src.application.usecases.unidades.listar_por_linea import ListarUnidadesPorLineaUseCase
from src.application.usecases.usuarios.actualizar_rol import ActualizarRolUseCase
from src.application.usecases.usuarios.eliminar import EliminarUsuarioUseCase
from src.application.usecases.usuarios.listar import ListarUsuariosUseCase
from src.domain.entities.usuario import Usuario
from src.domain.value_objects import Rol
from src.infrastructure.security.jwt import generar_token
from src.infrastructure.security.pin_hasher import PinHasher
from tests.fakes import make_repos, wire


@pytest.fixture
def repos():
    r = wire(make_repos())
    return r


@pytest.fixture
def api(monkeypatch, repos):
    r = repos

    # Override JWT auth to use fake repos.
    monkeypatch.setattr(jwt_module, "_usuario_repository", lambda: r.usuarios)

    import src.presentation.views.auth as va
    import src.presentation.views.linea as vl
    import src.presentation.views.punto_control as vp
    import src.presentation.views.solicitud_registro as vs
    import src.presentation.views.unidad as vu
    import src.presentation.views.usuario as vus

    va.login_use_case = lambda: LoginUseCase(r.usuarios, r.solicitudes)
    va.registro_use_case = lambda: RegistroUseCase(r.usuarios, r.solicitudes, r.lineas)

    vl.listar_lineas_use_case = lambda: ListarLineasUseCase(r.lineas)
    vl.obtener_linea_use_case = lambda: ObtenerLineaUseCase(r.lineas)
    vl.crear_linea_use_case = lambda: CrearLineaUseCase(r.lineas)
    vl.actualizar_linea_use_case = lambda: ActualizarLineaUseCase(r.lineas)
    vl.eliminar_linea_use_case = lambda: EliminarLineaUseCase(r.lineas)

    vp.listar_puntos_control_use_case = lambda: ListarPuntosControlUseCase(r.lineas, r.puntos)

    vs.listar_solicitudes_use_case = lambda: ListarSolicitudesUseCase(r.solicitudes)
    vs.crear_cambio_ruta_use_case = lambda: CrearCambioRutaUseCase(
        r.solicitudes, r.usuarios, r.lineas
    )
    vs.resolver_solicitud_use_case = lambda: ResolverSolicitudUseCase(
        r.solicitudes, r.usuarios, r.lineas
    )

    vu.listar_unidades_use_case = lambda: ListarUnidadesUseCase(r.unidades)
    vu.crear_unidad_use_case = lambda: CrearUnidadUseCase(r.unidades, r.lineas)
    vu.actualizar_unidad_use_case = lambda: ActualizarUnidadUseCase(r.unidades, r.lineas)
    vu.eliminar_unidad_use_case = lambda: EliminarUnidadUseCase(r.unidades)
    vu.listar_unidades_por_linea_use_case = lambda: ListarUnidadesPorLineaUseCase(
        r.unidades, r.lineas
    )

    vus.listar_usuarios_use_case = lambda: ListarUsuariosUseCase(r.usuarios)
    vus.actualizar_rol_use_case = lambda: ActualizarRolUseCase(r.usuarios)
    vus.eliminar_usuario_use_case = lambda: EliminarUsuarioUseCase(r.usuarios)
    vus.usuario_repository = lambda: r.usuarios

    from rest_framework.test import APIClient

    # Seed a default admin user and set its token.
    uid = uuid4()
    admin = Usuario(
        id=uid,
        nombre="Admin Test",
        dni="99999999",
        telefono="999999999",
        email="admin@test.com",
        foto_url=None,
        rol=Rol.ADMIN,
        is_online=False,
        created_at=datetime.now(UTC),
    )
    r.usuarios.seed(admin, PinHasher.hash("1234"))
    token = generar_token(admin)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    return r, client
