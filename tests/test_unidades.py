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
    uc = CrearUnidadUseCase(repos.unidades, repos.lineas)
    u = uc.ejecutar(CrearUnidadDTO(placa="ABC-123", linea_id=linea.id))
    assert u.id is not None
    assert u.placa == "ABC-123"


def test_crear_placa_vacia(repos):
    linea = _linea(repos)
    uc = CrearUnidadUseCase(repos.unidades, repos.lineas)
    with pytest.raises(ValidacionError):
        uc.ejecutar(CrearUnidadDTO(placa="   ", linea_id=linea.id))


def test_crear_linea_inexistente(repos):
    uc = CrearUnidadUseCase(repos.unidades, repos.lineas)
    with pytest.raises(NoEncontradoError):
        uc.ejecutar(CrearUnidadDTO(placa="ABC-123", linea_id=999))


def test_crear_placa_duplicada(repos):
    linea = _linea(repos)
    uc = CrearUnidadUseCase(repos.unidades, repos.lineas)
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
    uc = ActualizarUnidadUseCase(repos.unidades, repos.lineas)
    updated = uc.ejecutar(u.id, ActualizarUnidadDTO(estado="INACTIVA"))
    assert updated.estado == EstadoUnidad.INACTIVA


def test_actualizar_no_existe(repos):
    uc = ActualizarUnidadUseCase(repos.unidades, repos.lineas)
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
    with pytest.raises(ConflictoError):
        uc.ejecutar(u.id)


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
