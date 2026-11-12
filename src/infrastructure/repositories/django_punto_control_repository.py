from django.db.models.expressions import RawSQL

from src.domain.entities.punto_control import PuntoControl
from src.domain.repositories.punto_control_repository import PuntoControlRepository
from src.infrastructure.mappers.punto_control_mapper import PuntoControlMapper
from src.infrastructure.models.punto_control import PuntoControl as PuntoControlModel


class DjangoPuntoControlRepository(PuntoControlRepository):
    def find_by_linea(self, linea_id: int) -> list[PuntoControl]:
        modelos = (
            PuntoControlModel.objects.filter(linea_id=linea_id)
            .annotate(
                lat=RawSQL("ST_Y(ubicacion)", []),
                lng=RawSQL("ST_X(ubicacion)", []),
            )
            .order_by("orden")
        )
        return [PuntoControlMapper.to_domain(modelo) for modelo in modelos]
