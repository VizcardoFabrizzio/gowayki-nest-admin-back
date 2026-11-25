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
from src.presentation.permissions import EsAdminOJefeRuta
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
        "subrutaId": unidad.subruta_id,
        "subrutaCodigo": unidad.subruta_codigo,
        "estado": unidad.estado.value,
        "posicionActual": posicion,
    }


def _linea_id_jefe(request) -> int | None:
    usuario = getattr(request, "user", None)
    if getattr(usuario, "rol", None) == "JEFE_RUTA":
        return getattr(usuario, "linea_id", None)
    return None


class UnidadListView(APIView):
    permission_classes = [EsAdminOJefeRuta]

    @extend_schema(responses=UnidadSerializer(many=True))
    def get(self, request):
        unidades = listar_unidades_use_case().ejecutar()
        linea_jefe = _linea_id_jefe(request)
        if linea_jefe is not None:
            unidades = [u for u in unidades if u.linea_id == linea_jefe]
        return Response([_unidad_json(unidad) for unidad in unidades])

    @extend_schema(request=CrearUnidadSerializer, responses={201: UnidadSerializer})
    def post(self, request):
        datos = CrearUnidadSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        linea_id = datos.validated_data["lineaId"]
        linea_jefe = _linea_id_jefe(request)
        if linea_jefe is not None:
            linea_id = linea_jefe
        unidad = crear_unidad_use_case().ejecutar(
            CrearUnidadDTO(
                numero_padron=datos.validated_data.get("numeroPadron", ""),
                placa=datos.validated_data["placa"],
                linea_id=linea_id,
                estado=datos.validated_data.get("estado", "OPERATIVA"),
                subruta_id=datos.validated_data.get("subrutaId"),
            )
        )
        return Response(_unidad_json(unidad), status=status.HTTP_201_CREATED)


class UnidadDetailView(APIView):
    permission_classes = [EsAdminOJefeRuta]

    @extend_schema(request=ActualizarUnidadSerializer, responses=UnidadSerializer)
    def patch(self, request, unidad_id: int):
        datos = ActualizarUnidadSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        linea_jefe = _linea_id_jefe(request)
        if linea_jefe is not None:
            unidad_actual = listar_unidades_use_case().ejecutar()
            unidad_actual = next((u for u in unidad_actual if u.id == unidad_id), None)
            if unidad_actual is None or unidad_actual.linea_id != linea_jefe:
                return Response(
                    {"detail": "No tiene permiso para modificar esta combi."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        unidad = actualizar_unidad_use_case().ejecutar(
            unidad_id,
            ActualizarUnidadDTO(
                numero_padron=datos.validated_data.get("numeroPadron"),
                placa=datos.validated_data.get("placa"),
                linea_id=linea_jefe
                if linea_jefe is not None
                else datos.validated_data.get("lineaId"),
                estado=datos.validated_data.get("estado"),
                subruta_id=datos.validated_data.get("subrutaId"),
                subruta_id_presente="subrutaId" in request.data,
            ),
        )
        return Response(_unidad_json(unidad))

    @extend_schema(responses={200: None, 204: None})
    def delete(self, request, unidad_id: int):
        linea_jefe = _linea_id_jefe(request)
        if linea_jefe is not None:
            unidades = listar_unidades_use_case().ejecutar()
            unidad = next((u for u in unidades if u.id == unidad_id), None)
            if unidad is None or unidad.linea_id != linea_jefe:
                return Response(
                    {"detail": "No tiene permiso para eliminar esta combi."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        resultado = eliminar_unidad_use_case().ejecutar(unidad_id)
        if resultado == "desactivada":
            return Response(
                {
                    "detail": "La combi tiene historial asociado, se desactivó en lugar de eliminarse."
                },
                status=status.HTTP_200_OK,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class UnidadPorLineaListView(APIView):
    permission_classes = [EsAdminOJefeRuta]

    @extend_schema(responses=UnidadSerializer(many=True))
    def get(self, request, linea_id: int):
        linea_jefe = _linea_id_jefe(request)
        if linea_jefe is not None and linea_id != linea_jefe:
            return Response(
                {"detail": "No tiene permiso para consultar esta línea."},
                status=status.HTTP_403_FORBIDDEN,
            )
        unidades = listar_unidades_por_linea_use_case().ejecutar(
            ListarUnidadesPorLineaDTO(linea_id=linea_id)
        )
        return Response([_unidad_json(unidad) for unidad in unidades])
