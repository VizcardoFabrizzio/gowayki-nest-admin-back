from datetime import UTC, datetime

import pytest
from rest_framework import status

from src.application.dtos.linea import ActualizarLineaDTO, CrearLineaDTO
from src.application.usecases.lineas.actualizar import ActualizarLineaUseCase
from src.application.usecases.lineas.crear import CrearLineaUseCase
from src.application.usecases.lineas.eliminar import EliminarLineaUseCase
from src.application.usecases.lineas.listar import ListarLineasUseCase
from src.application.usecases.lineas.obtener import ObtenerLineaUseCase
from src.domain.entities.linea import Linea
from src.domain.exceptions import ConflictoError, NoEncontradoError, ValidacionError


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
    uc = CrearLineaUseCase(repos.lineas)
    linea = uc.ejecutar(CrearLineaDTO(nombre="Nueva", color_hex="#00FF00"))
    assert linea.id is not None
    assert linea.nombre == "Nueva"


def test_crear_nombre_vacio(repos):
    uc = CrearLineaUseCase(repos.lineas)
    with pytest.raises(ValidacionError):
        uc.ejecutar(CrearLineaDTO(nombre="   "))


def test_listar(repos):
    _linea(repos)
    uc = ListarLineasUseCase(repos.lineas)
    assert len(uc.ejecutar()) == 1


def test_obtener_ok(repos):
    linea = _linea(repos)
    uc = ObtenerLineaUseCase(repos.lineas)
    assert uc.ejecutar(linea.id).nombre == "L1"


def test_obtener_no_existe(repos):
    uc = ObtenerLineaUseCase(repos.lineas)
    with pytest.raises(NoEncontradoError):
        uc.ejecutar(999)


def test_actualizar_ok(repos):
    linea = _linea(repos)
    uc = ActualizarLineaUseCase(repos.lineas)
    updated = uc.ejecutar(linea.id, ActualizarLineaDTO(nombre="Renombrada"))
    assert updated.nombre == "Renombrada"


def test_actualizar_no_existe(repos):
    uc = ActualizarLineaUseCase(repos.lineas)
    with pytest.raises(NoEncontradoError):
        uc.ejecutar(999, ActualizarLineaDTO(nombre="X"))


def test_eliminar_ok(repos):
    linea = _linea(repos)
    uc = EliminarLineaUseCase(repos.lineas)
    uc.ejecutar(linea.id)
    assert repos.lineas.find_by_id(linea.id) is None


def test_eliminar_no_existe(repos):
    uc = EliminarLineaUseCase(repos.lineas)
    with pytest.raises(NoEncontradoError):
        uc.ejecutar(999)


def test_eliminar_con_unidades(repos):
    linea = _linea(repos)
    # make has_unidades true by seeding a unidad
    from src.domain.entities.unidad import Unidad
    from src.domain.value_objects import EstadoUnidad

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
    uc = EliminarLineaUseCase(repos.lineas)
    with pytest.raises(ConflictoError):
        uc.ejecutar(linea.id)


# ---------- api ----------


def test_api_crear_linea(api):
    repos, client = api
    resp = client.post("/api/lineas", {"nombre": "Nueva", "colorHex": "#00FF00"}, format="json")
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.data["nombre"] == "Nueva"


def test_api_listar_lineas(api):
    repos, client = api
    _linea(repos)
    resp = client.get("/api/lineas")
    assert resp.status_code == status.HTTP_200_OK
    assert isinstance(resp.data, list)
    assert len(resp.data) == 1


def test_api_listar_lineas_sin_autenticacion(api):
    from rest_framework.test import APIClient

    repos, _client = api
    _linea(repos)
    publico = APIClient()

    resp = publico.get("/api/lineas")

    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data) == 1


def test_api_crear_linea_sin_autenticacion(api):
    from rest_framework.test import APIClient

    publico = APIClient()

    resp = publico.post("/api/lineas", {"nombre": "Nueva"}, format="json")

    assert resp.status_code in {
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    }


def test_api_eliminar_linea(api):
    repos, client = api
    linea = _linea(repos)
    resp = client.delete(f"/api/lineas/{linea.id}")
    assert resp.status_code == status.HTTP_204_NO_CONTENT
