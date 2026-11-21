from datetime import UTC, datetime
from uuid import uuid4

import pytest
from rest_framework import status

from src.application.dtos.auth import RegistroDTO
from src.application.usecases.auth.login import LoginUseCase
from src.application.usecases.auth.registro import RegistroUseCase
from src.domain.entities.linea import Linea
from src.domain.entities.usuario import Usuario
from src.domain.exceptions import (
    AccesoDenegadoError,
    ConflictoError,
    CredencialesInvalidasError,
    CuentaBloqueadaError,
)
from src.domain.value_objects import Rol
from src.infrastructure.security.pin_hasher import PinHasher


def _seed_user(repos, rol=Rol.ADMIN, dni="12345678", pin="1234", telefono="999999999"):
    uid = uuid4()
    user = Usuario(
        id=uid,
        nombre="Test",
        dni=dni,
        telefono=telefono,
        email="test@test.com",
        foto_url=None,
        rol=rol,
        is_online=False,
        created_at=datetime.now(UTC),
    )
    repos.usuarios.seed(user, PinHasher.hash(pin))
    return uid, user


def _linea(repos, nombre="L1"):
    return repos.lineas.save(
        Linea(
            id=None,
            nombre=nombre,
            origen="A",
            destino="B",
            corredor=None,
            color_hex="#FF0000",
            created_at=datetime.now(UTC),
        )
    )


# ---------- unit ----------


def test_login_ok(repos):
    _seed_user(repos)
    uc = LoginUseCase(repos.usuarios, repos.solicitudes)
    u = uc.ejecutar("12345678", "1234")
    assert u.is_online is True


def test_login_pin_incorrecto(repos):
    _seed_user(repos)
    uc = LoginUseCase(repos.usuarios, repos.solicitudes)
    with pytest.raises(CredencialesInvalidasError):
        uc.ejecutar("12345678", "9999")


def test_login_chofer_denegado(repos):
    _seed_user(repos, rol=Rol.CHOFER)
    uc = LoginUseCase(repos.usuarios, repos.solicitudes)
    with pytest.raises(AccesoDenegadoError):
        uc.ejecutar("12345678", "1234")


def test_login_bloqueo_tras_intentos(repos):
    _seed_user(repos)
    uc = LoginUseCase(repos.usuarios, repos.solicitudes)
    for _ in range(4):
        with pytest.raises(CredencialesInvalidasError):
            uc.ejecutar("12345678", "9999")
    with pytest.raises(CuentaBloqueadaError):
        uc.ejecutar("12345678", "9999")


def test_registro_ok(repos):
    linea = _linea(repos)
    uc = RegistroUseCase(repos.usuarios, repos.solicitudes, repos.lineas)
    s = uc.ejecutar(
        RegistroDTO(
            nombre="Juan",
            dni="11111111",
            telefono="987654321",
            email="j@x.com",
            pin="1234",
            linea_id=linea.id,
        )
    )
    assert s.estado.value == "PENDIENTE"


def test_registro_dni_duplicado(repos):
    linea = _linea(repos)
    uid = uuid4()
    repos.usuarios.seed(
        Usuario(
            id=uid,
            nombre="X",
            dni="11111111",
            telefono="111111111",
            email=None,
            foto_url=None,
            rol=Rol.ADMIN,
            is_online=False,
            created_at=datetime.now(UTC),
        ),
        PinHasher.hash("1234"),
    )
    uc = RegistroUseCase(repos.usuarios, repos.solicitudes, repos.lineas)
    with pytest.raises(ConflictoError):
        uc.ejecutar(
            RegistroDTO(
                nombre="Juan",
                dni="11111111",
                telefono="987654321",
                email=None,
                pin="1234",
                linea_id=linea.id,
            )
        )


# ---------- api ----------


def test_api_login_ok(api):
    repos, client = api
    _seed_user(repos)
    resp = client.post("/api/auth/login", {"dni": "12345678", "pin": "1234"}, format="json")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["exito"] is True


def test_api_login_invalido(api):
    repos, client = api
    _seed_user(repos)
    resp = client.post("/api/auth/login", {"dni": "12345678", "pin": "0000"}, format="json")
    assert resp.status_code in (
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_423_LOCKED,
        status.HTTP_400_BAD_REQUEST,
    )
    assert resp.data["exito"] is False
