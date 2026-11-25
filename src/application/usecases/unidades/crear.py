from datetime import UTC, datetime

from src.application.dtos.unidad import CrearUnidadDTO
from src.domain.entities.unidad import Unidad
from src.domain.exceptions import ConflictoError, NoEncontradoError, ValidacionError
from src.domain.repositories.linea_repository import LineaRepository
from src.domain.repositories.subruta_repository import SubrutaRepository
from src.domain.repositories.unidad_repository import UnidadRepository
from src.domain.value_objects import EstadoUnidad


class CrearUnidadUseCase:
    def __init__(
        self,
        unidades: UnidadRepository,
        lineas: LineaRepository,
        subrutas: SubrutaRepository,
    ) -> None:
        self._unidades = unidades
        self._lineas = lineas
        self._subrutas = subrutas

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
        if datos.subruta_id is not None and (
            self._subrutas.find_activa_de_linea(datos.subruta_id, datos.linea_id) is None
        ):
            raise NoEncontradoError(
                "La subruta no existe, no está activa o no pertenece a la línea."
            )

        unidad = Unidad(
            id=None,
            numero_padron=(datos.numero_padron or "").strip(),
            placa=placa,
            linea_id=datos.linea_id,
            subruta_id=datos.subruta_id,
            estado=EstadoUnidad.del_panel(datos.estado or "OPERATIVA"),
            created_at=datetime.now(UTC),
        )
        return self._unidades.save(unidad)
