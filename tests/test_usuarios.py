from dataclasses import replace
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from rest_framework import status

from src.application.dtos.usuario import ActualizarRolDTO, ActualizarSubrutaDTO
from src.application.usecases.usuarios.actualizar_rol import ActualizarRolUseCase
from src.application.usecases.usuarios.actualizar_subruta import ActualizarSubrutaUseCase
from src.application.usecases.usuarios.eliminar import EliminarUsuarioUseCase
from src.application.usecases.usuarios.listar import ListarUsuariosUseCase
from src.domain.entities.usuario import Usuario
from src.domain.exceptions import ConflictoError, NoEncontradoError, ValidacionError
from src.domain.value_objects import Rol
from src.infrastructure.security.jwt import generar_token
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


def test_actualizar_subruta_del_jefe(repos):
    uid = _seed(repos, rol=Rol.JEFE_RUTA)
    # El jefe ya tiene línea asignada en el panel.
    repos.usuarios._lineas_rel[uid] = 1
    uc = ActualizarSubrutaUseCase(repos.usuarios)

    actualizado = uc.ejecutar(uid, ActualizarSubrutaDTO(subruta_id=42))

    assert actualizado.subruta_id == 42


def test_actualizar_subruta_rechaza_chofer(repos):
    uid = _seed(repos, rol=Rol.CHOFER)
    uc = ActualizarSubrutaUseCase(repos.usuarios)
    with pytest.raises(ValidacionError):
        uc.ejecutar(uid, ActualizarSubrutaDTO(subruta_id=42))


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
    eliminado = repos.usuarios.find_by_id(uid)
    assert eliminado is not None
    assert eliminado.activo is False
    assert eliminado.eliminado_en is not None


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
    assert repos.usuarios.find_by_id(uid).activo is False

    lista = client.get("/api/usuarios")
    assert all(str(item["id"]) != str(uid) for item in lista.data)


def test_token_de_cuenta_inactiva_no_autentica(api):
    from rest_framework.test import APIClient

    repos, _client = api
    uid = _seed(repos, rol=Rol.JEFE_RUTA)
    EliminarUsuarioUseCase(repos.usuarios).ejecutar(uid)
    inactivo = repos.usuarios.find_by_id(uid)

    publico = APIClient()
    publico.credentials(HTTP_AUTHORIZATION=f"Bearer {generar_token(inactivo)}")

    resp = publico.get("/api/solicitudes-registro")

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def _seed_jefe(repos, dni, subruta_id):
    uid = uuid4()
    jefe = Usuario(
        id=uid,
        nombre="Jefe",
        dni=dni,
        telefono="911111111",
        email=None,
        foto_url=None,
        rol=Rol.JEFE_RUTA,
        is_online=False,
        created_at=datetime.now(UTC),
        linea_id=1,
        subruta_id=subruta_id,
    )
    repos.usuarios.seed(jefe, PinHasher.hash("1234"), linea_id=1, subruta_id=subruta_id)
    return uid, jefe


def test_api_jefe_listar_usuarios_de_su_linea(api):
    from rest_framework.test import APIClient

    repos, _client = api
    jefe_uid, jefe = _seed_jefe(repos, "33333333", 5)  # línea 1

    otro_uid = uuid4()
    otro = Usuario(
        id=otro_uid,
        nombre="Chofer de otra línea",
        dni="44444444",
        telefono="944444444",
        email=None,
        foto_url=None,
        rol=Rol.CHOFER,
        is_online=False,
        created_at=datetime.now(UTC),
        linea_id=2,
    )
    repos.usuarios.seed(otro, PinHasher.hash("1234"), linea_id=2)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {generar_token(jefe)}")

    resp = client.get("/api/usuarios")

    assert resp.status_code == status.HTTP_200_OK
    ids = {item["id"] for item in resp.data}
    assert str(jefe_uid) in ids
    assert str(otro_uid) not in ids
    assert all(item["lineaId"] == 1 for item in resp.data)


def test_api_jefe_cambia_su_propia_subruta(api):
    repos, client = api
    uid, jefe = _seed_jefe(repos, "11111111", 5)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {generar_token(jefe)}")

    resp = client.patch(f"/api/usuarios/{uid}/subruta", {"subrutaId": 6}, format="json")

    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["subrutaDbId"] == 6


def test_repositorio_django_listar_usuarios_incluye_subruta(monkeypatch):
    from src.infrastructure.models.usuario import Usuario as UsuarioModel
    from src.infrastructure.repositories.django_usuario_repository import (
        DjangoUsuarioRepository,
    )

    uid = uuid4()
    modelo = UsuarioModel(
        id=uid,
        nombre="Jefe",
        dni="12345678",
        telefono="900000000",
        pin_hash="x",
        rol="JEFE_RUTA",
        created_at=datetime.now(UTC),
        activo=True,
        eliminado_en=None,
    )

    class FakeQuery:
        def filter(self, **kwargs):
            return self

        def order_by(self, *args):
            return [modelo]

    consulta = FakeQuery()
    monkeypatch.setattr(UsuarioModel.objects, "filter", lambda **kwargs: consulta)
    monkeypatch.setattr(UsuarioModel.objects, "order_by", lambda *args: consulta)
    monkeypatch.setattr(
        DjangoUsuarioRepository,
        "_lineas_por_usuario",
        lambda self, ids: {uid: (1, "Cono Norte", 5, "4A: Ciudad de Dios → Terminal")},
    )

    usuarios = DjangoUsuarioRepository().find_all()

    assert len(usuarios) == 1
    assert usuarios[0].linea_id == 1
    assert usuarios[0].subruta_id == 5
    assert usuarios[0].subruta_nombre == "4A: Ciudad de Dios → Terminal"


def test_api_jefe_no_puede_cambiar_la_subruta_de_otro(api):
    repos, client = api
    uid, jefe = _seed_jefe(repos, "11111111", 5)
    otro_uid, _ = _seed_jefe(repos, "22222222", 7)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {generar_token(jefe)}")

    resp = client.patch(f"/api/usuarios/{otro_uid}/subruta", {"subrutaId": 6}, format="json")

    assert resp.status_code == status.HTTP_403_FORBIDDEN


# ---------- regresiones de la auditoría ----------


def test_token_con_version_vieja_no_autentica(api):
    from rest_framework.test import APIClient

    repos, _client = api
    uid = _seed(repos, rol=Rol.JEFE_RUTA)
    actual = repos.usuarios.find_by_id(uid)
    token_viejo = generar_token(replace(actual, token_version=actual.token_version + 1))

    publico = APIClient()
    publico.credentials(HTTP_AUTHORIZATION=f"Bearer {token_viejo}")

    resp = publico.get("/api/solicitudes-registro")

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_repositorio_django_asignar_subruta_valida_linea_del_jefe(monkeypatch):
    from src.infrastructure.models.linea import Linea as LineaModel
    from src.infrastructure.models.subruta import Subruta as SubrutaModel
    from src.infrastructure.models.usuario_linea import UsuarioLinea as UsuarioLineaModel
    from src.infrastructure.repositories.django_usuario_repository import (
        DjangoUsuarioRepository,
    )

    uid = uuid4()
    fila = UsuarioLineaModel(usuario_id=uid, linea_id=1)
    linea = LineaModel(
        id=1,
        nombre="L1 Terminal",
        origen="A",
        destino="B",
        color_hex="#FF0000",
        created_at=datetime.now(UTC),
    )
    # Activa, pero de la línea L2: no puede asignarse a un jefe de la L1.
    subruta = SubrutaModel(id=5, codigo="S5", nombre="Subruta 5", linea_codigo="L2", activa=True)

    class FilaQuery:
        def filter(self, **kwargs):
            return self

        def first(self):
            return fila

    class LineaQuery:
        def filter(self, **kwargs):
            return self

        def first(self):
            return linea

    class SubrutaQuery:
        def filter(self, **kwargs):
            return self

        def first(self):
            return subruta

    monkeypatch.setattr(UsuarioLineaModel.objects, "filter", lambda **kw: FilaQuery())
    monkeypatch.setattr(LineaModel.objects, "filter", lambda **kw: LineaQuery())
    monkeypatch.setattr(SubrutaModel.objects, "filter", lambda **kw: SubrutaQuery())

    with pytest.raises(ConflictoError):
        DjangoUsuarioRepository().asignar_subruta(uid, 5)
