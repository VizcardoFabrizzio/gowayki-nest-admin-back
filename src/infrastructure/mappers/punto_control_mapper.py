from src.domain.entities.punto_control import PuntoControl
from src.infrastructure.models.punto_control import PuntoControl as PuntoControlModel


class PuntoControlMapper:
    @staticmethod
    def to_domain(modelo: PuntoControlModel) -> PuntoControl:
        return PuntoControl(
            id=modelo.id,
            linea_id=modelo.linea_id,
            nombre=modelo.nombre,
            orden=modelo.orden,
            lat=float(modelo.lat),
            lng=float(modelo.lng),
            radio_tolerancia_metros=modelo.radio_tolerancia_metros,
            tolerancia_minutos=modelo.tolerancia_minutos,
            created_at=modelo.created_at,
        )

    @staticmethod
    def to_orm(punto: PuntoControl) -> PuntoControlModel:
        return PuntoControlModel(
            id=punto.id,
            linea_id=punto.linea_id,
            nombre=punto.nombre,
            orden=punto.orden,
            radio_tolerancia_metros=punto.radio_tolerancia_metros,
            tolerancia_minutos=punto.tolerancia_minutos,
            created_at=punto.created_at,
        )
