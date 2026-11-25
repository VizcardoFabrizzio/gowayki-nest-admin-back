from datetime import UTC, datetime

from src.application.dtos.solicitud_registro import CrearCambioRutaDTO
from src.domain.entities.solicitud_registro import SolicitudRegistro
from src.domain.exceptions import NoEncontradoError, ValidacionError
from src.domain.repositories.linea_repository import LineaRepository
from src.domain.repositories.solicitud_registro_repository import (
    SolicitudRegistroRepository,
)
from src.domain.repositories.subruta_repository import SubrutaRepository
from src.domain.repositories.usuario_repository import UsuarioRepository
from src.domain.value_objects import EstadoSolicitud, Rol, TipoSolicitud


class CrearCambioRutaUseCase:
    def __init__(
        self,
        solicitudes: SolicitudRegistroRepository,
        usuarios: UsuarioRepository,
        lineas: LineaRepository,
        subrutas: SubrutaRepository,
    ) -> None:
        self._solicitudes = solicitudes
        self._usuarios = usuarios
        self._lineas = lineas
        self._subrutas = subrutas

    def ejecutar(self, datos: CrearCambioRutaDTO) -> SolicitudRegistro:
        if (datos.tipo or "").strip().upper() != TipoSolicitud.CAMBIO_RUTA.value:
            raise ValidacionError("El tipo debe ser CAMBIO_RUTA.")
        if datos.usuario_id is None:
            raise ValidacionError("El usuario es obligatorio.")
        if datos.linea_solicitada_id is None:
            raise ValidacionError("La línea solicitada es obligatoria.")
        if datos.subruta_solicitada_id is None:
            raise ValidacionError("La subruta solicitada es obligatoria.")

        usuario = self._usuarios.find_by_id(datos.usuario_id)
        if usuario is None:
            raise NoEncontradoError("El usuario no existe.")
        if usuario.rol not in (Rol.JEFE_RUTA, Rol.CHOFER):
            raise ValidacionError("Solo un jefe de ruta o un chofer puede solicitar el cambio.")

        linea = self._lineas.find_by_id(datos.linea_solicitada_id)
        if linea is None:
            raise NoEncontradoError("La línea no existe.")
        if (
            self._subrutas.find_activa_de_linea(
                datos.subruta_solicitada_id, datos.linea_solicitada_id
            )
            is None
        ):
            raise NoEncontradoError(
                "La subruta no existe, no está activa o no pertenece a la línea."
            )

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
            subruta_solicitada_id=datos.subruta_solicitada_id,
            usuario_id=usuario.id,
            pin_hash=None,
            estado=EstadoSolicitud.PENDIENTE,
            creado_en=ahora,
            actualizado_en=ahora,
        )
        return self._solicitudes.save(solicitud)
