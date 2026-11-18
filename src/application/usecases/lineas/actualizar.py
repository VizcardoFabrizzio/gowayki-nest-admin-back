from dataclasses import replace

from src.application.dtos.linea import ActualizarLineaDTO
from src.domain.entities.linea import Linea
from src.domain.exceptions import NoEncontradoError, ValidacionError
from src.domain.repositories.linea_repository import LineaRepository
from src.domain.value_objects import ColorHex


class ActualizarLineaUseCase:
    def __init__(self, repositorio: LineaRepository) -> None:
        self._repositorio = repositorio

    def ejecutar(self, linea_id: int, datos: ActualizarLineaDTO) -> Linea:
        linea = self._repositorio.find_by_id(linea_id)
        if linea is None:
            raise NoEncontradoError("La línea no existe.")

        cambios: dict[str, object] = {}
        if datos.nombre is not None:
            nombre = datos.nombre.strip()
            if not nombre:
                raise ValidacionError("El nombre de la línea es obligatorio.")
            cambios["nombre"] = nombre
        if datos.origen is not None:
            cambios["origen"] = datos.origen.strip()
        if datos.destino is not None:
            cambios["destino"] = datos.destino.strip()
        if datos.corredor is not None:
            corredor = datos.corredor.strip()
            cambios["corredor"] = corredor or None
        if datos.color_hex is not None:
            cambios["color_hex"] = str(ColorHex(datos.color_hex))

        if not cambios:
            return linea
        return self._repositorio.save(replace(linea, **cambios))
