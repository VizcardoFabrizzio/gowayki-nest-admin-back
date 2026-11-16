from src.domain.entities.solicitud_registro import SolicitudRegistro
from src.domain.value_objects import EstadoSolicitud, TipoSolicitud
from src.infrastructure.models.solicitud_registro import (
    SolicitudRegistro as SolicitudRegistroModel,
)


class SolicitudRegistroMapper:
    @staticmethod
    def to_domain(modelo: SolicitudRegistroModel) -> SolicitudRegistro:
        return SolicitudRegistro(
            id=modelo.id,
            tipo=TipoSolicitud(modelo.tipo),
            dni=modelo.dni,
            nombre_completo=modelo.nombre_completo,
            telefono=modelo.telefono,
            email=modelo.email,
            ruta_trabajo=modelo.ruta_trabajo,
            linea_solicitada_id=modelo.linea_solicitada_id,
            pin_hash=modelo.pin_hash,
            estado=EstadoSolicitud(modelo.estado),
            creado_en=modelo.creado_en,
        )

    @staticmethod
    def to_orm(solicitud: SolicitudRegistro) -> SolicitudRegistroModel:
        return SolicitudRegistroModel(
            id=solicitud.id,
            tipo=solicitud.tipo.value,
            dni=solicitud.dni,
            nombre_completo=solicitud.nombre_completo,
            telefono=solicitud.telefono,
            email=solicitud.email,
            ruta_trabajo=solicitud.ruta_trabajo,
            linea_solicitada_id=solicitud.linea_solicitada_id,
            pin_hash=solicitud.pin_hash,
            estado=solicitud.estado.value,
            creado_en=solicitud.creado_en,
            actualizado_en=solicitud.creado_en,
        )
