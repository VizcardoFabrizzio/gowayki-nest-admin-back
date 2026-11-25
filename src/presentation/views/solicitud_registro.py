from uuid import UUID

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from src.application.dtos.solicitud_registro import (
    CrearCambioRutaDTO,
    ListarSolicitudesDTO,
    ResolverSolicitudDTO,
)
from src.domain.entities.solicitud_registro import SolicitudRegistro
from src.infrastructure.container import (
    crear_cambio_ruta_use_case,
    listar_solicitudes_use_case,
    resolver_solicitud_use_case,
)
from src.presentation.permissions import EsAdmin, EsAdminOJefeRuta
from src.presentation.serializers.solicitud_registro import (
    CrearCambioRutaSerializer,
    ResolverSolicitudSerializer,
    SolicitudRegistroSerializer,
)


def _solicitud_json(solicitud: SolicitudRegistro) -> dict:
    return {
        "id": solicitud.id,
        "tipo": solicitud.tipo.value,
        "dni": solicitud.dni,
        "nombreCompleto": solicitud.nombre_completo,
        "telefono": solicitud.telefono,
        "placaNumero": solicitud.placa_numero,
        "rutaTrabajo": solicitud.ruta_trabajo,
        "lineaSolicitadaId": solicitud.linea_solicitada_id,
        "subrutaSolicitadaId": solicitud.subruta_solicitada_id,
        "usuarioId": str(solicitud.usuario_id) if solicitud.usuario_id else None,
        "estado": solicitud.estado.value,
        "usuarioAsignado": solicitud.usuario_asignado,
        "creadoEn": solicitud.creado_en,
        "actualizadoEn": solicitud.actualizado_en,
    }


class SolicitudRegistroListView(APIView):
    permission_classes = [EsAdminOJefeRuta]

    @extend_schema(responses=SolicitudRegistroSerializer(many=True))
    def get(self, request):
        usuario = request.user
        rol = getattr(usuario, "rol", "")

        # El jefe de ruta SIEMPRE usa la subruta de su token: el query param
        # del cliente no es confiable y permitiría ver solicitudes ajenas.
        subruta_id = None
        if rol == "JEFE_RUTA":
            subruta_id = getattr(usuario, "subruta_id", None)
        else:
            subruta_raw = request.query_params.get("subrutaId")
            if subruta_raw is not None and subruta_raw != "":
                try:
                    subruta_id = int(subruta_raw)
                except (TypeError, ValueError):
                    return Response(
                        {"exito": False, "mensaje": "La subruta no es válida."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        solicitudes = listar_solicitudes_use_case().ejecutar(
            ListarSolicitudesDTO(rol=rol, subruta_id=subruta_id)
        )
        return Response([_solicitud_json(s) for s in solicitudes])

    @extend_schema(request=CrearCambioRutaSerializer, responses={201: SolicitudRegistroSerializer})
    def post(self, request):
        datos = CrearCambioRutaSerializer(data=request.data)
        datos.is_valid(raise_exception=True)

        usuario = request.user
        usuario_id = getattr(usuario, "id", None)
        if usuario_id is None:
            return Response(
                {"exito": False, "mensaje": "El usuario no es válido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            usuario_uuid = UUID(str(usuario_id))
        except (ValueError, AttributeError):
            return Response(
                {"exito": False, "mensaje": "El usuario no es válido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        solicitud = crear_cambio_ruta_use_case().ejecutar(
            CrearCambioRutaDTO(
                tipo=datos.validated_data["tipo"],
                usuario_id=usuario_uuid,
                linea_solicitada_id=datos.validated_data["lineaSolicitadaId"],
                subruta_solicitada_id=datos.validated_data["subrutaSolicitadaId"],
            )
        )
        return Response(_solicitud_json(solicitud), status=status.HTTP_201_CREATED)


class SolicitudRegistroDetailView(APIView):
    # Aprobar o rechazar solicitudes es potestad exclusiva del administrador.
    permission_classes = [EsAdmin]

    @extend_schema(request=ResolverSolicitudSerializer, responses=SolicitudRegistroSerializer)
    def patch(self, request, solicitud_id: int):
        datos = ResolverSolicitudSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        solicitud = resolver_solicitud_use_case().ejecutar(
            solicitud_id,
            ResolverSolicitudDTO(
                estado=datos.validated_data["estado"],
                usuario_asignado=datos.validated_data.get("usuarioAsignado"),
            ),
        )
        return Response(_solicitud_json(solicitud))
