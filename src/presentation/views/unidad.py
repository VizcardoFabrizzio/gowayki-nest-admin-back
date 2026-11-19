from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from src.application.dtos.unidad import (
    ActualizarUnidadDTO,
    CrearUnidadDTO,
    ListarUnidadesPorLineaDTO,
)
from src.domain.entities.unidad import Unidad
from src.infrastructure.container import (
    actualizar_unidad_use_case,
    crear_unidad_use_case,
    eliminar_unidad_use_case,
    listar_unidades_por_linea_use_case,
    listar_unidades_use_case,
)
from src.presentation.serializers.unidad import (
    ActualizarUnidadSerializer,
    CrearUnidadSerializer,
    UnidadSerializer,
)


def _unidad_json(unidad: Unidad) -> dict:
    posicion = None
    if unidad.posicion_actual is not None:
        posicion = {
            "lat": unidad.posicion_actual.lat,
            "lng": unidad.posicion_actual.lng,
            "velocidadKmh": unidad.posicion_actual.velocidad_kmh,
            "rumboGrados": unidad.posicion_actual.rumbo_grados,
            "ultimaActualizacion": unidad.posicion_actual.ultima_actualizacion,
        }
    return {
        "id": unidad.id,
        "numeroPadron": unidad.numero_padron,
        "placa": unidad.placa,
        "lineaId": unidad.linea_id,
        "lineaNombre": unidad.linea_nombre,
        "estado": unidad.estado.value,
        "posicionActual": posicion,
    }


class UnidadListView(APIView):
    @extend_schema(responses=UnidadSerializer(many=True))
    def get(self, request):
        unidades = listar_unidades_use_case().ejecutar()
        return Response([_unidad_json(unidad) for unidad in unidades])

    @extend_schema(request=CrearUnidadSerializer, responses={201: UnidadSerializer})
    def post(self, request):
        datos = CrearUnidadSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        unidad = crear_unidad_use_case().ejecutar(
            CrearUnidadDTO(
                numero_padron=datos.validated_data.get("numeroPadron", ""),
                placa=datos.validated_data["placa"],
                linea_id=datos.validated_data["lineaId"],
                estado=datos.validated_data.get("estado", "OPERATIVA"),
            )
        )
        return Response(_unidad_json(unidad), status=status.HTTP_201_CREATED)


class UnidadDetailView(APIView):
    @extend_schema(request=ActualizarUnidadSerializer, responses=UnidadSerializer)
    def patch(self, request, unidad_id: int):
        datos = ActualizarUnidadSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        unidad = actualizar_unidad_use_case().ejecutar(
            unidad_id,
            ActualizarUnidadDTO(
                numero_padron=datos.validated_data.get("numeroPadron"),
                placa=datos.validated_data.get("placa"),
                linea_id=datos.validated_data.get("lineaId"),
                estado=datos.validated_data.get("estado"),
            ),
        )
        return Response(_unidad_json(unidad))

    @extend_schema(responses={204: None})
    def delete(self, request, unidad_id: int):
        eliminar_unidad_use_case().ejecutar(unidad_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UnidadPorLineaListView(APIView):
    @extend_schema(responses=UnidadSerializer(many=True))
    def get(self, request, linea_id: int):
        unidades = listar_unidades_por_linea_use_case().ejecutar(
            ListarUnidadesPorLineaDTO(linea_id=linea_id)
        )
        return Response([_unidad_json(unidad) for unidad in unidades])
