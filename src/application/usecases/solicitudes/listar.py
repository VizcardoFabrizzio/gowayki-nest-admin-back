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
            # El admin ve TODAS las solicitudes, incluidas las de choferes.
            return list(solicitudes)

        if datos.subruta_id is None:
            raise ValidacionError("La subruta es obligatoria para el jefe de ruta.")
        return [
            solicitud
            for solicitud in solicitudes
            if solicitud.estado.value == "PENDIENTE"
            and solicitud.tipo in (TipoSolicitud.CHOFER, TipoSolicitud.CAMBIO_RUTA)
            and solicitud.subruta_solicitada_id == datos.subruta_id
        ]
