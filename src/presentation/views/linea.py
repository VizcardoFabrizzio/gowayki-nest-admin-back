from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from src.application.dtos.linea import ActualizarLineaDTO, CrearLineaDTO
from src.domain.entities.linea import Linea
from src.infrastructure.container import (
    actualizar_linea_use_case,
    crear_linea_use_case,
    eliminar_linea_use_case,
    listar_lineas_use_case,
    obtener_linea_use_case,
)
from src.presentation.serializers.linea import (
    ActualizarLineaSerializer,
    CrearLineaSerializer,
    LineaSerializer,
)


def _linea_json(linea: Linea) -> dict:
    return {
        "id": linea.id,
        "nombre": linea.nombre,
        "origen": linea.origen,
        "destino": linea.destino,
        "corredor": linea.corredor,
        "colorHex": linea.color_hex,
    }


class LineaListView(APIView):
    @extend_schema(responses=LineaSerializer(many=True))
    def get(self, request):
        lineas = listar_lineas_use_case().ejecutar()
        return Response([_linea_json(linea) for linea in lineas])

    @extend_schema(request=CrearLineaSerializer, responses={201: LineaSerializer})
    def post(self, request):
        datos = CrearLineaSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        linea = crear_linea_use_case().ejecutar(
            CrearLineaDTO(
                nombre=datos.validated_data["nombre"],
                origen=datos.validated_data.get("origen", ""),
                destino=datos.validated_data.get("destino", ""),
                corredor=datos.validated_data.get("corredor"),
                color_hex=datos.validated_data.get("colorHex") or "#E53E3E",
            )
        )
        return Response(_linea_json(linea), status=status.HTTP_201_CREATED)


class LineaDetailView(APIView):
    @extend_schema(responses=LineaSerializer)
    def get(self, request, linea_id: int):
        linea = obtener_linea_use_case().ejecutar(linea_id)
        return Response(_linea_json(linea))

    @extend_schema(request=ActualizarLineaSerializer, responses=LineaSerializer)
    def patch(self, request, linea_id: int):
        datos = ActualizarLineaSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        linea = actualizar_linea_use_case().ejecutar(
            linea_id,
            ActualizarLineaDTO(
                nombre=datos.validated_data.get("nombre"),
                origen=datos.validated_data.get("origen"),
                destino=datos.validated_data.get("destino"),
                corredor=datos.validated_data.get("corredor"),
                color_hex=datos.validated_data.get("colorHex"),
            ),
        )
        return Response(_linea_json(linea))

    @extend_schema(responses={204: None})
    def delete(self, request, linea_id: int):
        eliminar_linea_use_case().ejecutar(linea_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
