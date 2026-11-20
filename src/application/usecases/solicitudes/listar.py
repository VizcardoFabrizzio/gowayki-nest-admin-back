from src.application.dtos.solicitud_registro import ListarSolicitudesDTO
from src.domain.entities.solicitud_registro import SolicitudRegistro
from src.domain.exceptions import ValidacionError
from src.domain.repositories.solicitud_registro_repository import (
    SolicitudRegistroRepository,
)
from src.domain.value_objects import TipoSolicitud


class ListarSolicitudesUseCase:
    def __init__(self, repositorio: SolicitudRegistroRepository) -> None:
        self._repositorio = repositorio

    def ejecutar(self, datos: ListarSolicitudesDTO) -> list[SolicitudRegistro]:
        rol = (datos.rol or "").strip().upper()
        if rol not in {"ADMIN", "JEFE_RUTA"}:
            raise ValidacionError("El rol debe ser ADMIN o JEFE_RUTA.")

        solicitudes = self._repositorio.find_all()

        if rol == "ADMIN":
            return [
                solicitud for solicitud in solicitudes if solicitud.tipo is not TipoSolicitud.CHOFER
            ]

        if datos.linea_id is None:
            raise ValidacionError("La línea es obligatoria para el jefe de ruta.")
        return [
            solicitud
            for solicitud in solicitudes
            if solicitud.tipo is TipoSolicitud.CHOFER
            and solicitud.linea_solicitada_id == datos.linea_id
        ]
