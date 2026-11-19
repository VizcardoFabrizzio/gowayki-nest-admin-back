from src.domain.entities.unidad import Unidad
from src.domain.value_objects import EstadoUnidad, PosicionGps
from src.infrastructure.models.unidad import Unidad as UnidadModel


class UnidadMapper:
    @staticmethod
    def to_domain(modelo: UnidadModel) -> Unidad:
        posicion = None
        lat = getattr(modelo, "posicion_lat", None)
        if lat is not None:
            posicion = PosicionGps(
                lat=float(lat),
                lng=float(modelo.posicion_lng),
                velocidad_kmh=float(modelo.posicion_velocidad),
                rumbo_grados=int(modelo.posicion_rumbo),
                ultima_actualizacion=modelo.posicion_actualizada,
            )

        return Unidad(
            id=modelo.id,
            numero_padron=modelo.numero_padron,
            placa=modelo.placa,
            linea_id=modelo.linea_id,
            estado=EstadoUnidad(modelo.estado),
            created_at=modelo.created_at,
            linea_nombre=modelo.linea.nombre if modelo.linea_id else None,
            posicion_actual=posicion,
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
