from src.domain.entities.unidad import Unidad
from src.domain.value_objects import EstadoUnidad
from src.infrastructure.models.unidad import Unidad as UnidadModel


class UnidadMapper:
    @staticmethod
    def to_domain(modelo: UnidadModel) -> Unidad:
        return Unidad(
            id=modelo.id,
            numero_padron=modelo.numero_padron,
            placa=modelo.placa,
            linea_id=modelo.linea_id,
            estado=EstadoUnidad(modelo.estado),
            created_at=modelo.created_at,
        )

    @staticmethod
    def to_orm(unidad: Unidad) -> UnidadModel:
        return UnidadModel(
            id=unidad.id,
            numero_padron=unidad.numero_padron,
            placa=unidad.placa,
            linea_id=unidad.linea_id,
            estado=unidad.estado.value,
            created_at=unidad.created_at,
        )
