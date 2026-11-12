from src.domain.entities.linea import Linea
from src.infrastructure.models.linea import Linea as LineaModel


class LineaMapper:
    @staticmethod
    def to_domain(modelo: LineaModel) -> Linea:
        return Linea(
            id=modelo.id,
            nombre=modelo.nombre,
            origen=modelo.origen,
            destino=modelo.destino,
            corredor=modelo.corredor,
            color_hex=modelo.color_hex,
            created_at=modelo.created_at,
        )

    @staticmethod
    def to_orm(linea: Linea) -> LineaModel:
        return LineaModel(
            id=linea.id,
            nombre=linea.nombre,
            origen=linea.origen,
            destino=linea.destino,
            corredor=linea.corredor,
            color_hex=linea.color_hex,
            created_at=linea.created_at,
        )
