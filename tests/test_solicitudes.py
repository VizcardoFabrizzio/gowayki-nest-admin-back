from datetime import UTC, datetime
from uuid import uuid4

import pytest
from rest_framework import status

from src.application.dtos.solicitud_registro import (
    CrearCambioRutaDTO,
    ListarSolicitudesDTO,
    ResolverSolicitudDTO,
)
from src.application.usecases.solicitudes.crear_cambio_ruta import CrearCambioRutaUseCase
from src.application.usecases.solicitudes.listar import ListarSolicitudesUseCase
from src.application.usecases.solicitudes.resolver import ResolverSolicitudUseCase
from src.domain.entities.linea import Linea
from src.domain.entities.solicitud_registro import SolicitudRegistro
from src.domain.entities.subruta import Subruta
from src.domain.entities.usuario import Usuario
from src.domain.exceptions import ConflictoError, NoEncontradoError, ValidacionError
from src.domain.value_objects import EstadoSolicitud, Rol, TipoSolicitud
from src.infrastructure.security.pin_hasher import PinHasher


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


def _user(repos, rol=Rol.JEFE_RUTA, dni="12345678", linea_id=None):
    uid = uuid4()
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
        linea_id=linea_id,
    )
    repos.usuarios.seed(user, PinHasher.hash("1234"), linea_id=linea_id)
    return uid, user


def _jefe(repos, subruta_id=None, dni="33333333"):
    uid = uuid4()
    user = Usuario(
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
    repos.usuarios.seed(user, PinHasher.hash("1234"), linea_id=1, subruta_id=subruta_id)
    return uid, user


def test_listar_admin_filtra_chofer(repos):
    # seed a chofer solicitud and a jefe solicitud
    repos.solicitudes.save(
        SolicitudRegistro(
            id=None,
            tipo=TipoSolicitud.CHOFER,
            dni="11111111",
            nombre_completo="C",
            estado=EstadoSolicitud.PENDIENTE,
            creado_en=datetime.now(UTC),
            telefono="900000000",
        )
    )
    repos.solicitudes.save(
        SolicitudRegistro(
            id=None,
            tipo=TipoSolicitud.JEFE_RUTA,
            dni="22222222",
            nombre_completo="J",
            estado=EstadoSolicitud.PENDIENTE,
            creado_en=datetime.now(UTC),
            telefono="900000001",
        )
    )
    uc = ListarSolicitudesUseCase(repos.solicitudes)
    res = uc.ejecutar(ListarSolicitudesDTO(rol="ADMIN"))
    # El admin ve TODAS, incluidas las solicitudes de chofer.
    assert len(res) == 2
    assert {s.tipo for s in res} == {TipoSolicitud.CHOFER, TipoSolicitud.JEFE_RUTA}


def test_listar_rol_invalido(repos):
    uc = ListarSolicitudesUseCase(repos.solicitudes)
    with pytest.raises(ValidacionError):
        uc.ejecutar(ListarSolicitudesDTO(rol="CHOFER"))


def test_listar_jefe_requiere_linea(repos):
    uc = ListarSolicitudesUseCase(repos.solicitudes)
    with pytest.raises(ValidacionError):
        uc.ejecutar(ListarSolicitudesDTO(rol="JEFE_RUTA"))


def test_crear_cambio_ruta_ok(repos):
    uid, user = _user(repos)
    linea = _linea(repos)
    uc = CrearCambioRutaUseCase(repos.solicitudes, repos.usuarios, repos.lineas, repos.subrutas)
    s = uc.ejecutar(
        CrearCambioRutaDTO(
            tipo="CAMBIO_RUTA",
            usuario_id=uid,
            linea_solicitada_id=linea.id,
            subruta_solicitada_id=1,
        )
    )
    assert s.tipo == TipoSolicitud.CAMBIO_RUTA
    assert s.estado == EstadoSolicitud.PENDIENTE


def test_crear_cambio_ruta_usuario_no_jefe(repos):
    uid, user = _user(repos, rol=Rol.ADMIN)
    linea = _linea(repos)
    uc = CrearCambioRutaUseCase(repos.solicitudes, repos.usuarios, repos.lineas, repos.subrutas)
    with pytest.raises(ValidacionError):
        uc.ejecutar(
            CrearCambioRutaDTO(
                tipo="CAMBIO_RUTA",
                usuario_id=uid,
                linea_solicitada_id=linea.id,
                subruta_solicitada_id=1,
            )
        )


def test_crear_cambio_ruta_tipo_invalido(repos):
    uid, user = _user(repos)
    linea = _linea(repos)
    uc = CrearCambioRutaUseCase(repos.solicitudes, repos.usuarios, repos.lineas, repos.subrutas)
    with pytest.raises(ValidacionError):
        uc.ejecutar(CrearCambioRutaDTO(tipo="OTRO", usuario_id=uid, linea_solicitada_id=linea.id))


def test_resolver_rechazar(repos):
    s = repos.solicitudes.save(
        SolicitudRegistro(
            id=None,
            tipo=TipoSolicitud.JEFE_RUTA,
            dni="33333333",
            nombre_completo="J",
            estado=EstadoSolicitud.PENDIENTE,
            creado_en=datetime.now(UTC),
            telefono="900000002",
            pin_hash="hash",
            linea_solicitada_id=None,
        )
    )
    uc = ResolverSolicitudUseCase(
        repos.solicitudes, repos.usuarios, repos.lineas, repos.transacciones, repos.subrutas
    )
    res = uc.ejecutar(s.id, ResolverSolicitudDTO(estado="RECHAZADA"))
    assert res.estado == EstadoSolicitud.RECHAZADA


def test_resolver_ya_resuelta(repos):
    s = repos.solicitudes.save(
        SolicitudRegistro(
            id=None,
            tipo=TipoSolicitud.JEFE_RUTA,
            dni="33333333",
            nombre_completo="J",
            estado=EstadoSolicitud.APROBADA,
            creado_en=datetime.now(UTC),
            telefono="900000002",
        )
    )
    uc = ResolverSolicitudUseCase(
        repos.solicitudes, repos.usuarios, repos.lineas, repos.transacciones, repos.subrutas
    )
    with pytest.raises(ConflictoError):
        uc.ejecutar(s.id, ResolverSolicitudDTO(estado="RECHAZADA"))


def test_resolver_aprobar_jefe_ruta_crea_usuario(repos):
    linea = _linea(repos)
    s = repos.solicitudes.save(
        SolicitudRegistro(
            id=None,
            tipo=TipoSolicitud.JEFE_RUTA,
            dni="44444444",
            nombre_completo="Jefe",
            estado=EstadoSolicitud.PENDIENTE,
            creado_en=datetime.now(UTC),
            telefono="900000003",
            email="j@x.com",
            pin_hash="hashpin",
            linea_solicitada_id=linea.id,
        )
    )
    uc = ResolverSolicitudUseCase(
        repos.solicitudes, repos.usuarios, repos.lineas, repos.transacciones, repos.subrutas
    )
    res = uc.ejecutar(s.id, ResolverSolicitudDTO(estado="APROBADA"))
    assert res.estado == EstadoSolicitud.APROBADA
    # usuario creado
    assert repos.usuarios.find_by_dni("44444444") is not None


def test_resolver_reactiva_cuenta_dada_de_baja(repos):
    linea = _linea(repos)
    uid = uuid4()
    repos.usuarios.seed(
        Usuario(
            id=uid,
            nombre="Baja",
            dni="44444444",
            telefono="900000003",
            email="j@x.com",
            foto_url=None,
            rol=Rol.JEFE_RUTA,
            is_online=False,
            created_at=datetime.now(UTC),
            activo=False,
            eliminado_en=datetime.now(UTC),
        ),
        PinHasher.hash("1234"),
    )
    s = repos.solicitudes.save(
        SolicitudRegistro(
            id=None,
            tipo=TipoSolicitud.JEFE_RUTA,
            dni="44444444",
            nombre_completo="Jefe reactivado",
            estado=EstadoSolicitud.PENDIENTE,
            creado_en=datetime.now(UTC),
            telefono="900000003",
            email="j@x.com",
            pin_hash="hashpin",
            linea_solicitada_id=linea.id,
            usuario_id=uid,
        )
    )
    uc = ResolverSolicitudUseCase(
        repos.solicitudes, repos.usuarios, repos.lineas, repos.transacciones, repos.subrutas
    )

    res = uc.ejecutar(s.id, ResolverSolicitudDTO(estado="APROBADA"))

    reactivado = repos.usuarios.find_by_id(uid)
    assert res.estado == EstadoSolicitud.APROBADA
    assert reactivado.id == uid
    assert reactivado.activo is True
    assert reactivado.eliminado_en is None
    assert reactivado.reactivado_en is not None
    assert reactivado.nombre == "Jefe reactivado"


def test_resolver_aprobar_sin_pin(repos):
    s = repos.solicitudes.save(
        SolicitudRegistro(
            id=None,
            tipo=TipoSolicitud.JEFE_RUTA,
            dni="55555555",
            nombre_completo="J",
            estado=EstadoSolicitud.PENDIENTE,
            creado_en=datetime.now(UTC),
            telefono="900000004",
            pin_hash=None,
            linea_solicitada_id=None,
        )
    )
    uc = ResolverSolicitudUseCase(
        repos.solicitudes, repos.usuarios, repos.lineas, repos.transacciones, repos.subrutas
    )
    with pytest.raises(ValidacionError):
        uc.ejecutar(s.id, ResolverSolicitudDTO(estado="APROBADA"))


def test_resolver_cambio_ruta_aprueba(repos):
    uid, user = _user(repos, linea_id=1)
    l2 = _linea(repos, nombre="L2")
    s = repos.solicitudes.save(
        SolicitudRegistro(
            id=None,
            tipo=TipoSolicitud.CAMBIO_RUTA,
            dni=user.dni,
            nombre_completo=user.nombre,
            estado=EstadoSolicitud.PENDIENTE,
            creado_en=datetime.now(UTC),
            telefono=user.telefono,
            usuario_id=uid,
            linea_solicitada_id=l2.id,
        )
    )
    uc = ResolverSolicitudUseCase(
        repos.solicitudes, repos.usuarios, repos.lineas, repos.transacciones, repos.subrutas
    )
    res = uc.ejecutar(s.id, ResolverSolicitudDTO(estado="APROBADA"))
    assert res.estado == EstadoSolicitud.APROBADA


# ---------- api ----------


def test_api_listar_solicitudes(api):
    repos, client = api
    repos.solicitudes.save(
        SolicitudRegistro(
            id=None,
            tipo=TipoSolicitud.JEFE_RUTA,
            dni="22222222",
            nombre_completo="J",
            estado=EstadoSolicitud.PENDIENTE,
            creado_en=datetime.now(UTC),
            telefono="900000001",
        )
    )
    resp = client.get("/api/solicitudes-registro?rol=ADMIN")
    assert resp.status_code == status.HTTP_200_OK
    assert isinstance(resp.data, list)


def test_api_crear_cambio_ruta(api):
    repos, client = api
    uid, user = _user(repos)
    linea = _linea(repos)
    from src.infrastructure.security.jwt import generar_token

    token = generar_token(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    resp = client.post(
        "/api/solicitudes-registro",
        {
            "tipo": "CAMBIO_RUTA",
            "lineaSolicitadaId": linea.id,
            "subrutaSolicitadaId": 1,
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED


def test_api_resolver_solicitud(api):
    repos, client = api
    linea = _linea(repos)
    s = repos.solicitudes.save(
        SolicitudRegistro(
            id=None,
            tipo=TipoSolicitud.JEFE_RUTA,
            dni="44444444",
            nombre_completo="Jefe",
            estado=EstadoSolicitud.PENDIENTE,
            creado_en=datetime.now(UTC),
            telefono="900000003",
            email="j@x.com",
            pin_hash="hashpin",
            linea_solicitada_id=linea.id,
        )
    )
    resp = client.patch(f"/api/solicitudes-registro/{s.id}", {"estado": "APROBADA"}, format="json")
    assert resp.status_code == status.HTTP_200_OK


# ---------- regresiones de la auditoría ----------


def test_api_jefe_no_puede_resolver_solicitud(api):
    from rest_framework.test import APIClient

    from src.infrastructure.security.jwt import generar_token

    repos, _client = api
    _, jefe = _jefe(repos, subruta_id=1)
    s = repos.solicitudes.save(
        SolicitudRegistro(
            id=None,
            tipo=TipoSolicitud.JEFE_RUTA,
            dni="44444444",
            nombre_completo="Jefe",
            estado=EstadoSolicitud.PENDIENTE,
            creado_en=datetime.now(UTC),
            telefono="900000003",
            pin_hash="hashpin",
            linea_solicitada_id=1,
        )
    )
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {generar_token(jefe)}")

    resp = client.patch(f"/api/solicitudes-registro/{s.id}", {"estado": "APROBADA"}, format="json")

    assert resp.status_code == status.HTTP_403_FORBIDDEN
    assert repos.solicitudes.find_by_id(s.id).estado is EstadoSolicitud.PENDIENTE


def test_api_jefe_ignora_subruta_del_query_param(api):
    from rest_framework.test import APIClient

    from src.infrastructure.security.jwt import generar_token

    repos, _client = api
    _, jefe = _jefe(repos, subruta_id=1)
    propia = repos.solicitudes.save(
        SolicitudRegistro(
            id=None,
            tipo=TipoSolicitud.CHOFER,
            dni="11111111",
            nombre_completo="Propio",
            estado=EstadoSolicitud.PENDIENTE,
            creado_en=datetime.now(UTC),
            telefono="900000010",
            subruta_solicitada_id=1,
        )
    )
    ajena = repos.solicitudes.save(
        SolicitudRegistro(
            id=None,
            tipo=TipoSolicitud.CHOFER,
            dni="22222222",
            nombre_completo="Ajena",
            estado=EstadoSolicitud.PENDIENTE,
            creado_en=datetime.now(UTC),
            telefono="900000011",
            subruta_solicitada_id=355,
        )
    )
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {generar_token(jefe)}")

    resp = client.get("/api/solicitudes-registro?subrutaId=355")

    assert resp.status_code == status.HTTP_200_OK
    ids = [item["id"] for item in resp.data]
    assert propia.id in ids
    assert ajena.id not in ids


def test_crear_cambio_ruta_valida_subruta(repos):
    uid, _ = _user(repos)
    linea = _linea(repos)
    uc = CrearCambioRutaUseCase(repos.solicitudes, repos.usuarios, repos.lineas, repos.subrutas)
    datos = dict(
        tipo="CAMBIO_RUTA",
        usuario_id=uid,
        linea_solicitada_id=linea.id,
    )
    # Inexistente.
    with pytest.raises(NoEncontradoError):
        uc.ejecutar(CrearCambioRutaDTO(**datos, subruta_solicitada_id=999))
    # De otra línea.
    with pytest.raises(NoEncontradoError):
        uc.ejecutar(CrearCambioRutaDTO(**datos, subruta_solicitada_id=7))
    # Inactiva.
    repos.subrutas.seed(
        Subruta(id=99, codigo="SR-99", nombre="SR 99", linea_codigo="L1", activa=False)
    )
    with pytest.raises(NoEncontradoError):
        uc.ejecutar(CrearCambioRutaDTO(**datos, subruta_solicitada_id=99))


def test_resolver_agrupa_escrituras_en_una_transaccion(repos, monkeypatch):
    linea = _linea(repos)
    s = repos.solicitudes.save(
        SolicitudRegistro(
            id=None,
            tipo=TipoSolicitud.JEFE_RUTA,
            dni="55555555",
            nombre_completo="J",
            estado=EstadoSolicitud.PENDIENTE,
            creado_en=datetime.now(UTC),
            telefono="900000012",
            pin_hash="hashpin",
            linea_solicitada_id=linea.id,
        )
    )
    uc = ResolverSolicitudUseCase(
        repos.solicitudes, repos.usuarios, repos.lineas, repos.transacciones, repos.subrutas
    )
    writes = []
    guardar_solicitud = repos.solicitudes.save
    guardar_usuario = repos.usuarios.save

    def solicitudes_save(solicitud):
        writes.append(("solicitud", repos.transacciones.activo))
        return guardar_solicitud(solicitud)

    def usuarios_save(usuario, **kwargs):
        writes.append(("usuario", repos.transacciones.activo))
        return guardar_usuario(usuario, **kwargs)

    monkeypatch.setattr(repos.solicitudes, "save", solicitudes_save)
    monkeypatch.setattr(repos.usuarios, "save", usuarios_save)

    uc.ejecutar(s.id, ResolverSolicitudDTO(estado="APROBADA"))

    assert repos.transacciones.llamadas == 1
    assert writes == [("usuario", True), ("solicitud", True)]


def test_resolver_rechaza_contacto_de_usuario_inactivo_ajeno(repos):
    _linea(repos)
    uid = uuid4()
    repos.usuarios.seed(
        Usuario(
            id=uid,
            nombre="Baja",
            dni="44444445",
            telefono="900000013",
            email=None,
            foto_url=None,
            rol=Rol.JEFE_RUTA,
            is_online=False,
            created_at=datetime.now(UTC),
            activo=False,
        ),
        PinHasher.hash("1234"),
    )
    s = repos.solicitudes.save(
        SolicitudRegistro(
            id=None,
            tipo=TipoSolicitud.JEFE_RUTA,
            dni="44444446",
            nombre_completo="J",
            estado=EstadoSolicitud.PENDIENTE,
            creado_en=datetime.now(UTC),
            telefono="900000013",
            pin_hash="hashpin",
            linea_solicitada_id=1,
        )
    )
    uc = ResolverSolicitudUseCase(
        repos.solicitudes, repos.usuarios, repos.lineas, repos.transacciones, repos.subrutas
    )
    with pytest.raises(ConflictoError):
        uc.ejecutar(s.id, ResolverSolicitudDTO(estado="APROBADA"))


def test_resolver_rechaza_subruta_de_otra_linea(repos):
    linea = _linea(repos)
    s = repos.solicitudes.save(
        SolicitudRegistro(
            id=None,
            tipo=TipoSolicitud.JEFE_RUTA,
            dni="55555556",
            nombre_completo="J",
            estado=EstadoSolicitud.PENDIENTE,
            creado_en=datetime.now(UTC),
            telefono="900000014",
            pin_hash="hashpin",
            linea_solicitada_id=linea.id,
            subruta_solicitada_id=7,  # subruta de L2
        )
    )
    uc = ResolverSolicitudUseCase(
        repos.solicitudes, repos.usuarios, repos.lineas, repos.transacciones, repos.subrutas
    )
    with pytest.raises(NoEncontradoError):
        uc.ejecutar(s.id, ResolverSolicitudDTO(estado="APROBADA"))


def test_listar_jefe_no_ve_solicitudes_destinadas_al_admin(repos):
    repos.solicitudes.save(
        SolicitudRegistro(
            id=None,
            tipo=TipoSolicitud.CAMBIO_RUTA,
            dni="44444444",
            nombre_completo="Cambio solicitado por un jefe",
            estado=EstadoSolicitud.PENDIENTE,
            creado_en=datetime.now(UTC),
            subruta_solicitada_id=1,
            usuario_asignado="ADMIN",
        )
    )
    uc = ListarSolicitudesUseCase(repos.solicitudes)
    assert uc.ejecutar(ListarSolicitudesDTO(rol="JEFE_RUTA", subruta_id=1)) == []
