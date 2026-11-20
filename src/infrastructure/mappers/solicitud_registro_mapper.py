from src.domain.entities.solicitud_registro import SolicitudRegistro
from src.domain.value_objects import EstadoSolicitud, TipoSolicitud
from src.infrastructure.models.solicitud_registro import (
    SolicitudRegistro as SolicitudRegistroModel,
)


class SolicitudRegistroMapper:
    @staticmethod
    def to_domain(modelo: SolicitudRegistroModel) -> SolicitudRegistro:
        actualizado = getattr(modelo, "actualizado_en", None)
        return SolicitudRegistro(
            id=modelo.id,
            tipo=TipoSolicitud(modelo.tipo),
            dni=modelo.dni,
            nombre_completo=modelo.nombre_completo,
            estado=EstadoSolicitud(modelo.estado),
            creado_en=modelo.creado_en,
            telefono=modelo.telefono,
            email=modelo.email,
            ruta_trabajo=modelo.ruta_trabajo,
            placa_numero=modelo.placa_numero,
            linea_solicitada_id=modelo.linea_solicitada_id,
            usuario_id=modelo.usuario_id,
            pin_hash=modelo.pin_hash,
            usuario_asignado=modelo.usuario_asignado,
            actualizado_en=actualizado,
        )

    @staticmethod
    def to_orm(solicitud: SolicitudRegistro) -> SolicitudRegistroModel:
        actualizado = solicitud.actualizado_en or solicitud.creado_en
        return SolicitudRegistroModel(
            id=solicitud.id,
            tipo=solicitud.tipo.value,
            dni=solicitud.dni,
            nombre_completo=solicitud.nombre_completo,
            telefono=solicitud.telefono,
            email=solicitud.email,
            ruta_trabajo=solicitud.ruta_trabajo,
            placa_numero=solicitud.placa_numero,
            linea_solicitada_id=solicitud.linea_solicitada_id,
            usuario_id=solicitud.usuario_id,
            pin_hash=solicitud.pin_hash,
            estado=solicitud.estado.value,
            usuario_asignado=solicitud.usuario_asignado,
            creado_en=solicitud.creado_en,
            actualizado_en=actualizado,
        )
