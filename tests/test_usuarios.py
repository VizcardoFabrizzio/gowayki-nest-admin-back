from datetime import UTC, datetime
from uuid import uuid4

import pytest
from rest_framework import status

from src.application.dtos.usuario import ActualizarRolDTO
from src.application.usecases.usuarios.actualizar_rol import ActualizarRolUseCase
from src.application.usecases.usuarios.eliminar import EliminarUsuarioUseCase
from src.application.usecases.usuarios.listar import ListarUsuariosUseCase
from src.domain.entities.usuario import Usuario
from src.domain.exceptions import ConflictoError, NoEncontradoError, ValidacionError
from src.domain.value_objects import Rol
from src.infrastructure.security.pin_hasher import PinHasher


def _seed(repos, rol=Rol.ADMIN, dni=None):
    uid = uuid4()
    dni = dni or str(uid.int)[:8].rjust(8, "0")
    user = Usuario(
        id=uid,
        nombre="U",
        dni=dni,
        telefono="900000000",
        email=None,
        foto_url=None,
        rol=rol,
        is_online=False,
        created_at=datetime.now(UTC),
    )
    repos.usuarios.seed(user, PinHasher.hash("1234"))
    return uid


def test_listar(repos):
    _seed(repos)
    uc = ListarUsuariosUseCase(repos.usuarios)
    assert len(uc.ejecutar()) == 1


def test_actualizar_rol_ok(repos):
    uid = _seed(repos, rol=Rol.JEFE_RUTA)
    uc = ActualizarRolUseCase(repos.usuarios)
    u = uc.ejecutar(uid, ActualizarRolDTO(rol="ADMIN"))
    assert u.rol == Rol.ADMIN


def test_actualizar_rol_ultimo_admin(repos):
    uid = _seed(repos, rol=Rol.ADMIN)
    uc = ActualizarRolUseCase(repos.usuarios)
    with pytest.raises(ConflictoError):
        uc.ejecutar(uid, ActualizarRolDTO(rol="JEFE_RUTA"))


def test_actualizar_rol_chofer_no_permitido(repos):
    uid = _seed(repos, rol=Rol.CHOFER)
    uc = ActualizarRolUseCase(repos.usuarios)
    with pytest.raises(ValidacionError):
        uc.ejecutar(uid, ActualizarRolDTO(rol="ADMIN"))


def test_actualizar_rol_no_existe(repos):
    uc = ActualizarRolUseCase(repos.usuarios)
    with pytest.raises(NoEncontradoError):
        uc.ejecutar(uuid4(), ActualizarRolDTO(rol="ADMIN"))


def test_eliminar_ok(repos):
    uid = _seed(repos, rol=Rol.JEFE_RUTA)
    uc = EliminarUsuarioUseCase(repos.usuarios)
    uc.ejecutar(uid)
    assert repos.usuarios.find_by_id(uid) is None


def test_eliminar_ultimo_admin(repos):
    uid = _seed(repos, rol=Rol.ADMIN)
    uc = EliminarUsuarioUseCase(repos.usuarios)
    with pytest.raises(ConflictoError):
        uc.ejecutar(uid)


def test_eliminar_no_existe(repos):
    uc = EliminarUsuarioUseCase(repos.usuarios)
    with pytest.raises(NoEncontradoError):
        uc.ejecutar(uuid4())


# ---------- api ----------


def test_api_listar_usuarios(api):
    repos, client = api
    _seed(repos)
    resp = client.get("/api/usuarios")
    assert resp.status_code == status.HTTP_200_OK
    assert isinstance(resp.data, list)
    assert len(resp.data) == 2


def test_api_actualizar_rol(api):
    repos, client = api
    uid = _seed(repos, rol=Rol.JEFE_RUTA)
    resp = client.patch(f"/api/usuarios/{uid}", {"rol": "ADMIN"}, format="json")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["rol"] == "ADMIN"


def test_api_eliminar_usuario(api):
    repos, client = api
    uid = _seed(repos, rol=Rol.JEFE_RUTA)
    resp = client.delete(f"/api/usuarios/{uid}")
    assert resp.status_code == status.HTTP_204_NO_CONTENT


def test_api_actualizar_subruta(api):
    repos, client = api
    uid = _seed(repos, rol=Rol.JEFE_RUTA)
    resp = client.patch(f"/api/usuarios/{uid}/subruta", {"subrutaId": 42}, format="json")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["id"] == str(uid)


def test_api_actualizar_subruta_no_existe(api):
    repos, client = api
    from uuid import uuid4

    resp = client.patch(f"/api/usuarios/{uuid4()}/subruta", {"subrutaId": 42}, format="json")
    assert resp.status_code == status.HTTP_404_NOT_FOUND
