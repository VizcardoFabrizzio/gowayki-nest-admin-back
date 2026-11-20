from src.domain.entities.solicitud_registro import SolicitudRegistro
from src.domain.repositories.solicitud_registro_repository import (
    SolicitudRegistroRepository,
)
from src.domain.value_objects import EstadoSolicitud
from src.infrastructure.mappers.solicitud_registro_mapper import (
    SolicitudRegistroMapper,
)
from src.infrastructure.models.solicitud_registro import (
    SolicitudRegistro as SolicitudRegistroModel,
)


class DjangoSolicitudRegistroRepository(SolicitudRegistroRepository):
    def find_all(self) -> list[SolicitudRegistro]:
        modelos = SolicitudRegistroModel.objects.order_by("-creado_en")
        return [SolicitudRegistroMapper.to_domain(modelo) for modelo in modelos]

    def find_by_id(self, solicitud_id: int) -> SolicitudRegistro | None:
        modelo = SolicitudRegistroModel.objects.filter(id=solicitud_id).first()
        return SolicitudRegistroMapper.to_domain(modelo) if modelo else None

    def save(self, solicitud: SolicitudRegistro) -> SolicitudRegistro:
        modelo = SolicitudRegistroMapper.to_orm(solicitud)
        modelo.save()
        return SolicitudRegistroMapper.to_domain(modelo)

    def find_pendiente_by_dni(self, dni: str) -> SolicitudRegistro | None:
        modelo = (
            SolicitudRegistroModel.objects.filter(
                dni=dni,
                estado=EstadoSolicitud.PENDIENTE.value,
            )
            .order_by("-creado_en")
            .first()
        )
        return SolicitudRegistroMapper.to_domain(modelo) if modelo else None
