from src.application.dtos.unidad import ListarUnidadesPorLineaDTO
from src.domain.entities.unidad import Unidad
from src.domain.exceptions import NoEncontradoError
from src.domain.repositories.linea_repository import LineaRepository
from src.domain.repositories.unidad_repository import UnidadRepository


class ListarUnidadesPorLineaUseCase:
    def __init__(
        self,
        unidades: UnidadRepository,
        lineas: LineaRepository,
    ) -> None:
        self._unidades = unidades
        self._lineas = lineas

    def ejecutar(self, datos: ListarUnidadesPorLineaDTO) -> list[Unidad]:
        if not self._lineas.exists_by_id(datos.linea_id):
            raise NoEncontradoError("La línea no existe.")
        return self._unidades.find_by_linea(datos.linea_id)
