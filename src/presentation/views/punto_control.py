from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from src.application.dtos.punto_control import ListarPuntosControlDTO
from src.domain.entities.punto_control import PuntoControl
from src.infrastructure.container import listar_puntos_control_use_case
from src.presentation.serializers.punto_control import PuntoControlSerializer


def _punto_json(punto: PuntoControl) -> dict:
    return {
        "id": punto.id,
        "nombre": punto.nombre,
        "orden": punto.orden,
        "lat": punto.lat,
        "lng": punto.lng,
        "radioMetros": punto.radio_tolerancia_metros,
        "toleranciaMinutos": punto.tolerancia_minutos,
    }


class PuntoControlListView(APIView):
    @extend_schema(responses=PuntoControlSerializer(many=True))
    def get(self, request, linea_id: int):
        puntos = listar_puntos_control_use_case().ejecutar(
            ListarPuntosControlDTO(linea_id=linea_id)
        )
        return Response([_punto_json(punto) for punto in puntos])
