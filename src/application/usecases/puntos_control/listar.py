from src.application.dtos.punto_control import ListarPuntosControlDTO
from src.domain.entities.punto_control import PuntoControl
from src.domain.exceptions import NoEncontradoError
from src.domain.repositories.linea_repository import LineaRepository
from src.domain.repositories.punto_control_repository import PuntoControlRepository


class ListarPuntosControlUseCase:
    def __init__(
        self,
        lineas: LineaRepository,
        puntos: PuntoControlRepository,
    ) -> None:
        self._lineas = lineas
        self._puntos = puntos

    def ejecutar(self, datos: ListarPuntosControlDTO) -> list[PuntoControl]:
        if not self._lineas.exists_by_id(datos.linea_id):
            raise NoEncontradoError("La línea no existe.")
        return self._puntos.find_by_linea(datos.linea_id)
