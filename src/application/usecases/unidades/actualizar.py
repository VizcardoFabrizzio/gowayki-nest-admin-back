from dataclasses import replace

from src.application.dtos.unidad import ActualizarUnidadDTO
from src.domain.entities.unidad import Unidad
from src.domain.exceptions import ConflictoError, NoEncontradoError, ValidacionError
from src.domain.repositories.linea_repository import LineaRepository
from src.domain.repositories.subruta_repository import SubrutaRepository
from src.domain.repositories.unidad_repository import UnidadRepository
from src.domain.value_objects import EstadoUnidad


class ActualizarUnidadUseCase:
    def __init__(
        self,
        unidades: UnidadRepository,
        lineas: LineaRepository,
        subrutas: SubrutaRepository,
    ) -> None:
        self._unidades = unidades
        self._lineas = lineas
        self._subrutas = subrutas

    def ejecutar(self, unidad_id: int, datos: ActualizarUnidadDTO) -> Unidad:
        unidad = self._unidades.find_by_id(unidad_id)
        if unidad is None:
            raise NoEncontradoError("La unidad no existe.")

        cambios: dict[str, object] = {}
        if datos.numero_padron is not None:
            cambios["numero_padron"] = datos.numero_padron.strip()
        if datos.placa is not None:
            placa = datos.placa.strip()
            if not placa:
                raise ValidacionError("La placa es obligatoria.")
            if self._unidades.exists_by_placa(placa, exclude_id=unidad_id):
                raise ConflictoError("La placa ya está registrada.")
            cambios["placa"] = placa
        if datos.linea_id is not None:
            if not self._lineas.exists_by_id(datos.linea_id):
                raise NoEncontradoError("La línea no existe.")
            cambios["linea_id"] = datos.linea_id
        # La clave puede llegar explícitamente en null: eso desasigna la subruta.
        if datos.subruta_id_presente:
            if datos.subruta_id is not None:
                linea_destino = datos.linea_id if datos.linea_id is not None else unidad.linea_id
                if self._subrutas.find_activa_de_linea(datos.subruta_id, linea_destino) is None:
                    raise NoEncontradoError(
                        "La subruta no existe, no está activa o no pertenece a la línea."
                    )
            cambios["subruta_id"] = datos.subruta_id
        if datos.estado is not None:
            cambios["estado"] = EstadoUnidad.del_panel(datos.estado)

        if not cambios:
            return unidad
        return self._unidades.save(replace(unidad, **cambios))
