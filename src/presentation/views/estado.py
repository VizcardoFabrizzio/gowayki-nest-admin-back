from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from src.presentation.serializers.estado import EstadoSerializer


class EstadoView(APIView):
    @extend_schema(responses=EstadoSerializer)
    def get(self, request):
        return Response(
            {
                "exito": True,
                "mensaje": "API en linea",
                "servicio": "gowayki-admin-api",
                "version": "0.1.0",
            }
        )
