from dataclasses import replace
from datetime import UTC, datetime
from uuid import uuid4

from src.application.dtos.solicitud_registro import ResolverSolicitudDTO
from src.domain.entities.solicitud_registro import SolicitudRegistro
from src.domain.entities.usuario import Usuario
from src.domain.exceptions import ConflictoError, NoEncontradoError, ValidacionError
from src.domain.repositories.linea_repository import LineaRepository
from src.domain.repositories.solicitud_registro_repository import (
    SolicitudRegistroRepository,
)
from src.domain.repositories.subruta_repository import SubrutaRepository
from src.domain.repositories.usuario_repository import UsuarioRepository
from src.domain.transacciones import GestorTransacciones
from src.domain.value_objects import EstadoSolicitud, Rol, TipoSolicitud


class ResolverSolicitudUseCase:
    def __init__(
        self,
        solicitudes: SolicitudRegistroRepository,
        usuarios: UsuarioRepository,
        lineas: LineaRepository,
        transacciones: GestorTransacciones,
        subrutas: SubrutaRepository,
    ) -> None:
        self._solicitudes = solicitudes
        self._usuarios = usuarios
        self._lineas = lineas
        self._transacciones = transacciones
        self._subrutas = subrutas

    def ejecutar(self, solicitud_id: int, datos: ResolverSolicitudDTO) -> SolicitudRegistro:
        solicitud = self._solicitudes.find_by_id(solicitud_id)
        if solicitud is None:
            raise NoEncontradoError("La solicitud no existe.")
        if solicitud.estado is not EstadoSolicitud.PENDIENTE:
            raise ConflictoError("La solicitud ya fue resuelta.")

        estado = (datos.estado or "").strip().upper()
        if estado not in {EstadoSolicitud.APROBADA.value, EstadoSolicitud.RECHAZADA.value}:
            raise ValidacionError("El estado debe ser APROBADA o RECHAZADA.")

        ahora = datetime.now(UTC)

        if estado == EstadoSolicitud.RECHAZADA.value:
            resuelta = replace(
                solicitud,
                estado=EstadoSolicitud.RECHAZADA,
                pin_hash=None,
                usuario_asignado=None,
                actualizado_en=ahora,
            )
            with self._transacciones.atomic():
                return self._solicitudes.save(resuelta)

        usuario_asignado = (datos.usuario_asignado or "").strip() or solicitud.dni

        if (
            solicitud.subruta_solicitada_id is not None
            and solicitud.linea_solicitada_id is not None
            and self._subrutas.find_activa_de_linea(
                solicitud.subruta_solicitada_id, solicitud.linea_solicitada_id
            )
            is None
        ):
            raise NoEncontradoError(
                "La subruta solicitada no existe, no está activa o no pertenece a la línea."
            )

        if solicitud.tipo is TipoSolicitud.CAMBIO_RUTA:
            if solicitud.usuario_id is None:
                raise ValidacionError("La solicitud no tiene usuario asociado.")
            if solicitud.linea_solicitada_id is None:
                raise ValidacionError("La solicitud no tiene línea solicitada.")
            if not self._lineas.exists_by_id(solicitud.linea_solicitada_id):
                raise NoEncontradoError("La línea no existe.")

            usuario = self._usuarios.find_by_id(solicitud.usuario_id)
            if usuario is None:
                raise NoEncontradoError("El usuario no existe.")

            # Las dos escrituras (usuario y solicitud) deben commit o rollback juntas.
            with self._transacciones.atomic():
                self._usuarios.save(
                    usuario,
                    linea_id=solicitud.linea_solicitada_id,
                    subruta_id=solicitud.subruta_solicitada_id,
                )
                resuelta = replace(
                    solicitud,
                    estado=EstadoSolicitud.APROBADA,
                    usuario_asignado=usuario_asignado,
                    actualizado_en=ahora,
                )
                return self._solicitudes.save(resuelta)

        if solicitud.pin_hash is None:
            raise ValidacionError("La solicitud no tiene PIN pendiente.")
        if not solicitud.telefono:
            raise ValidacionError("La solicitud no tiene teléfono.")

        rol = Rol.JEFE_RUTA if solicitud.tipo is TipoSolicitud.JEFE_RUTA else Rol.CHOFER

        # Si la cuenta fue dada de baja, la reactivamos conservando su id y
        # su historial; solo actualizamos los datos vigentes.
        existente = self._usuarios.find_by_dni(solicitud.dni)
        objetivo_id = solicitud.usuario_id or (existente.id if existente else None)
        # Un teléfono o email repetido bloquea la aprobación incluso si la otra
        # cuenta está dada de baja; solo se ignora la cuenta que se reactiva.
        if self._usuarios.exists_by_telefono(solicitud.telefono, exclude_id=objetivo_id):
            raise ConflictoError("El teléfono ya está registrado.")
        if solicitud.email and self._usuarios.exists_by_email(
            solicitud.email, exclude_id=objetivo_id
        ):
            raise ConflictoError("El email ya está registrado.")
        if objetivo_id is not None:
            usuario = self._usuarios.find_by_id(objetivo_id)
            if usuario is None:
                raise NoEncontradoError("El usuario a reactivar no existe.")
            usuario = replace(
                usuario,
                nombre=solicitud.nombre_completo or solicitud.dni,
                dni=solicitud.dni,
                telefono=solicitud.telefono,
                email=solicitud.email,
                rol=rol,
                is_online=False,
                activo=True,
                eliminado_en=None,
                reactivado_en=ahora,
            )
        else:
            usuario = Usuario(
                id=uuid4(),
                nombre=solicitud.nombre_completo or solicitud.dni,
                dni=solicitud.dni,
                telefono=solicitud.telefono,
                email=solicitud.email,
                foto_url=None,
                rol=rol,
                is_online=False,
                created_at=ahora,
            )

        with self._transacciones.atomic():
            self._usuarios.save(
                usuario,
                pin_hash=solicitud.pin_hash,
                linea_id=solicitud.linea_solicitada_id,
                subruta_id=solicitud.subruta_solicitada_id,
            )
            resuelta = replace(
                solicitud,
                estado=EstadoSolicitud.APROBADA,
                usuario_asignado=usuario_asignado,
                actualizado_en=ahora,
            )
            return self._solicitudes.save(resuelta)
