from datetime import UTC, datetime

import pytest
from rest_framework import status

from src.application.dtos.unidad import (
    ActualizarUnidadDTO,
    CrearUnidadDTO,
    ListarUnidadesPorLineaDTO,
)
from src.application.usecases.unidades.actualizar import ActualizarUnidadUseCase
from src.application.usecases.unidades.crear import CrearUnidadUseCase
from src.application.usecases.unidades.eliminar import EliminarUnidadUseCase
from src.application.usecases.unidades.listar import ListarUnidadesUseCase
from src.application.usecases.unidades.listar_por_linea import ListarUnidadesPorLineaUseCase
from src.domain.entities.linea import Linea
from src.domain.entities.unidad import Unidad
from src.domain.exceptions import ConflictoError, NoEncontradoError, ValidacionError
from src.domain.value_objects import EstadoUnidad


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


def test_crear_ok(repos):
    linea = _linea(repos)
    uc = CrearUnidadUseCase(repos.unidades, repos.lineas, repos.subrutas)
    u = uc.ejecutar(CrearUnidadDTO(placa="ABC-123", linea_id=linea.id))
    assert u.id is not None
    assert u.placa == "ABC-123"


def test_crear_guarda_subruta(repos):
    """La subruta elegida en el panel debe persistir para que la app la vea."""
    linea = _linea(repos)
    uc = CrearUnidadUseCase(repos.unidades, repos.lineas, repos.subrutas)
    u = uc.ejecutar(CrearUnidadDTO(placa="ABC-123", linea_id=linea.id, subruta_id=355))
    assert u.subruta_id == 355
    assert repos.unidades.find_by_id(u.id).subruta_id == 355


def test_crear_placa_vacia(repos):
    linea = _linea(repos)
    uc = CrearUnidadUseCase(repos.unidades, repos.lineas, repos.subrutas)
    with pytest.raises(ValidacionError):
        uc.ejecutar(CrearUnidadDTO(placa="   ", linea_id=linea.id))


def test_crear_linea_inexistente(repos):
    uc = CrearUnidadUseCase(repos.unidades, repos.lineas, repos.subrutas)
    with pytest.raises(NoEncontradoError):
        uc.ejecutar(CrearUnidadDTO(placa="ABC-123", linea_id=999))


def test_crear_placa_duplicada(repos):
    linea = _linea(repos)
    uc = CrearUnidadUseCase(repos.unidades, repos.lineas, repos.subrutas)
    uc.ejecutar(CrearUnidadDTO(placa="ABC-123", linea_id=linea.id))
    with pytest.raises(ConflictoError):
        uc.ejecutar(CrearUnidadDTO(placa="ABC-123", linea_id=linea.id))


def test_listar(repos):
    linea = _linea(repos)
    repos.unidades.save(
        Unidad(
            id=None,
            numero_padron="P1",
            placa="ABC-123",
            linea_id=linea.id,
            estado=EstadoUnidad.OPERATIVA,
            created_at=datetime.now(UTC),
        )
    )
    uc = ListarUnidadesUseCase(repos.unidades)
    assert len(uc.ejecutar()) == 1


def test_listar_por_linea_ok(repos):
    linea = _linea(repos)
    repos.unidades.save(
        Unidad(
            id=None,
            numero_padron="P1",
            placa="ABC-123",
            linea_id=linea.id,
            estado=EstadoUnidad.OPERATIVA,
            created_at=datetime.now(UTC),
        )
    )
    uc = ListarUnidadesPorLineaUseCase(repos.unidades, repos.lineas)
    assert len(uc.ejecutar(ListarUnidadesPorLineaDTO(linea_id=linea.id))) == 1


def test_listar_por_linea_linea_inexistente(repos):
    uc = ListarUnidadesPorLineaUseCase(repos.unidades, repos.lineas)
    with pytest.raises(NoEncontradoError):
        uc.ejecutar(ListarUnidadesPorLineaDTO(linea_id=999))


def test_actualizar_ok(repos):
    linea = _linea(repos)
    u = repos.unidades.save(
        Unidad(
            id=None,
            numero_padron="P1",
            placa="ABC-123",
            linea_id=linea.id,
            estado=EstadoUnidad.OPERATIVA,
            created_at=datetime.now(UTC),
        )
    )
    uc = ActualizarUnidadUseCase(repos.unidades, repos.lineas, repos.subrutas)
    updated = uc.ejecutar(u.id, ActualizarUnidadDTO(estado="BAJA"))
    assert updated.estado == EstadoUnidad.BAJA


def test_actualizar_guarda_subruta(repos):
    linea = _linea(repos)
    u = repos.unidades.save(
        Unidad(
            id=None,
            numero_padron="P1",
            placa="ABC-123",
            linea_id=linea.id,
            estado=EstadoUnidad.OPERATIVA,
            created_at=datetime.now(UTC),
        )
    )
    uc = ActualizarUnidadUseCase(repos.unidades, repos.lineas, repos.subrutas)
    updated = uc.ejecutar(u.id, ActualizarUnidadDTO(subruta_id=355, subruta_id_presente=True))
    assert updated.subruta_id == 355
    assert repos.unidades.find_by_id(u.id).subruta_id == 355


def test_actualizar_no_existe(repos):
    uc = ActualizarUnidadUseCase(repos.unidades, repos.lineas, repos.subrutas)
    with pytest.raises(NoEncontradoError):
        uc.ejecutar(999, ActualizarUnidadDTO(placa="X"))


def test_eliminar_ok(repos):
    linea = _linea(repos)
    u = repos.unidades.save(
        Unidad(
            id=None,
            numero_padron="P1",
            placa="ABC-123",
            linea_id=linea.id,
            estado=EstadoUnidad.OPERATIVA,
            created_at=datetime.now(UTC),
        )
    )
    uc = EliminarUnidadUseCase(repos.unidades)
    uc.ejecutar(u.id)
    assert repos.unidades.find_by_id(u.id) is None


def test_eliminar_no_existe(repos):
    uc = EliminarUnidadUseCase(repos.unidades)
    with pytest.raises(NoEncontradoError):
        uc.ejecutar(999)


def test_eliminar_con_registros(repos):
    linea = _linea(repos)
    u = repos.unidades.save(
        Unidad(
            id=None,
            numero_padron="P1",
            placa="ABC-123",
            linea_id=linea.id,
            estado=EstadoUnidad.OPERATIVA,
            created_at=datetime.now(UTC),
        )
    )
    repos.unidades.set_has_registros(u.id, True)
    uc = EliminarUnidadUseCase(repos.unidades)
    resultado = uc.ejecutar(u.id)
    assert resultado == "desactivada"
    assert repos.unidades.find_by_id(u.id).estado == EstadoUnidad.BAJA


# ---------- api ----------


def test_api_crear_unidad(api):
    repos, client = api
    linea = _linea(repos)
    resp = client.post("/api/unidades", {"placa": "ABC-123", "lineaId": linea.id}, format="json")
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.data["placa"] == "ABC-123"


def test_api_listar_unidades(api):
    repos, client = api
    linea = _linea(repos)
    repos.unidades.save(
        Unidad(
            id=None,
            numero_padron="P1",
            placa="ABC-123",
            linea_id=linea.id,
            estado=EstadoUnidad.OPERATIVA,
            created_at=datetime.now(UTC),
        )
    )
    resp = client.get("/api/unidades")
    assert resp.status_code == status.HTTP_200_OK
    assert isinstance(resp.data, list)
    assert len(resp.data) == 1


def test_api_eliminar_unidad(api):
    repos, client = api
    linea = _linea(repos)
    u = repos.unidades.save(
        Unidad(
            id=None,
            numero_padron="P1",
            placa="ABC-123",
            linea_id=linea.id,
            estado=EstadoUnidad.OPERATIVA,
            created_at=datetime.now(UTC),
        )
    )
    resp = client.delete(f"/api/unidades/{u.id}")
    assert resp.status_code == status.HTTP_204_NO_CONTENT


# ---------- regresiones de la auditoría ----------


def test_actualizar_limpia_subruta_con_null(repos):
    linea = _linea(repos)
    u = repos.unidades.save(
        Unidad(
            id=None,
            numero_padron="P1",
            placa="ABC-123",
            linea_id=linea.id,
            estado=EstadoUnidad.OPERATIVA,
            created_at=datetime.now(UTC),
            subruta_id=355,
        )
    )
    uc = ActualizarUnidadUseCase(repos.unidades, repos.lineas, repos.subrutas)

    actualizada = uc.ejecutar(u.id, ActualizarUnidadDTO(subruta_id=None, subruta_id_presente=True))

    assert actualizada.subruta_id is None
    assert repos.unidades.find_by_id(u.id).subruta_id is None


def test_api_actualizar_limpia_subruta_con_null(api):
    repos, client = api
    linea = _linea(repos)
    creada = client.post(
        "/api/unidades",
        {"placa": "ABC-123", "lineaId": linea.id, "subrutaId": 355},
        format="json",
    )
    assert creada.data["subrutaId"] == 355

    resp = client.patch(f"/api/unidades/{creada.data['id']}", {"subrutaId": None}, format="json")

    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["subrutaId"] is None
    assert repos.unidades.find_by_id(creada.data["id"]).subruta_id is None


def test_crear_unidad_rechaza_subruta_inexistente(repos):
    linea = _linea(repos)
    uc = CrearUnidadUseCase(repos.unidades, repos.lineas, repos.subrutas)
    with pytest.raises(NoEncontradoError):
        uc.ejecutar(CrearUnidadDTO(placa="ABC-123", linea_id=linea.id, subruta_id=999))


def test_api_unidad_incluye_subruta_codigo(api):
    repos, client = api
    linea = _linea(repos)
    resp = client.post(
        "/api/unidades",
        {"placa": "ABC-123", "lineaId": linea.id, "subrutaId": 355},
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.data["subrutaCodigo"] == "SR-355"


def test_estado_unidad_normaliza_alias_del_panel():
    assert EstadoUnidad.del_panel("EN MANTENIMIENTO") == EstadoUnidad.MANTENIMIENTO
    assert EstadoUnidad.del_panel("INACTIVA") == EstadoUnidad.BAJA
    assert EstadoUnidad.del_panel(" activa ") == EstadoUnidad.OPERATIVA
    with pytest.raises(ValidacionError):
        EstadoUnidad.del_panel("DESCONOCIDO")
