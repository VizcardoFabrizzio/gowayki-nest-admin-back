from datetime import UTC, datetime

from src.application.dtos.unidad import CrearUnidadDTO
from src.domain.entities.unidad import Unidad
from src.domain.exceptions import ConflictoError, NoEncontradoError, ValidacionError
from src.domain.repositories.linea_repository import LineaRepository
from src.domain.repositories.unidad_repository import UnidadRepository
from src.domain.value_objects import EstadoUnidad


class CrearUnidadUseCase:
    def __init__(
        self,
        unidades: UnidadRepository,
        lineas: LineaRepository,
    ) -> None:
        self._unidades = unidades
        self._lineas = lineas

    def ejecutar(self, datos: CrearUnidadDTO) -> Unidad:
        placa = (datos.placa or "").strip()
        if not placa:
            raise ValidacionError("La placa es obligatoria.")
        if datos.linea_id is None:
            raise ValidacionError("La línea es obligatoria.")
        if not self._lineas.exists_by_id(datos.linea_id):
            raise NoEncontradoError("La línea no existe.")
        if self._unidades.exists_by_placa(placa):
            raise ConflictoError("La placa ya está registrada.")

        unidad = Unidad(
            id=None,
            numero_padron=(datos.numero_padron or "").strip(),
            placa=placa,
            linea_id=datos.linea_id,
            estado=EstadoUnidad.del_panel(datos.estado or "OPERATIVA"),
            created_at=datetime.now(UTC),
        )
        return self._unidades.save(unidad)
