from datetime import UTC, datetime

from src.application.dtos.solicitud_registro import CrearCambioRutaDTO
from src.domain.entities.solicitud_registro import SolicitudRegistro
from src.domain.exceptions import NoEncontradoError, ValidacionError
from src.domain.repositories.linea_repository import LineaRepository
from src.domain.repositories.solicitud_registro_repository import (
    SolicitudRegistroRepository,
)
from src.domain.repositories.usuario_repository import UsuarioRepository
from src.domain.value_objects import EstadoSolicitud, Rol, TipoSolicitud


class CrearCambioRutaUseCase:
    def __init__(
        self,
        solicitudes: SolicitudRegistroRepository,
        usuarios: UsuarioRepository,
        lineas: LineaRepository,
    ) -> None:
        self._solicitudes = solicitudes
        self._usuarios = usuarios
        self._lineas = lineas

    def ejecutar(self, datos: CrearCambioRutaDTO) -> SolicitudRegistro:
        if (datos.tipo or "").strip().upper() != TipoSolicitud.CAMBIO_RUTA.value:
            raise ValidacionError("El tipo debe ser CAMBIO_RUTA.")
        if datos.usuario_id is None:
            raise ValidacionError("El usuario es obligatorio.")
        if datos.linea_solicitada_id is None:
            raise ValidacionError("La línea solicitada es obligatoria.")

        usuario = self._usuarios.find_by_id(datos.usuario_id)
        if usuario is None:
            raise NoEncontradoError("El usuario no existe.")
        if usuario.rol is not Rol.JEFE_RUTA:
            raise ValidacionError("Solo un jefe de ruta puede solicitar el cambio.")

        linea = self._lineas.find_by_id(datos.linea_solicitada_id)
        if linea is None:
            raise NoEncontradoError("La línea no existe.")

        ahora = datetime.now(UTC)
        solicitud = SolicitudRegistro(
            id=None,
            tipo=TipoSolicitud.CAMBIO_RUTA,
            dni=usuario.dni,
            nombre_completo=usuario.nombre,
            telefono=usuario.telefono,
            email=usuario.email,
            ruta_trabajo=linea.nombre,
            linea_solicitada_id=linea.id,
            usuario_id=usuario.id,
            pin_hash=None,
            estado=EstadoSolicitud.PENDIENTE,
            creado_en=ahora,
            actualizado_en=ahora,
        )
        return self._solicitudes.save(solicitud)
