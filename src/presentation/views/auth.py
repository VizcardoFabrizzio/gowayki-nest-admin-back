from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from src.application.dtos.auth import RegistroDTO
from src.domain.entities.usuario import Usuario
from src.infrastructure.container import login_use_case, registro_use_case
from src.infrastructure.security.jwt import generar_token
from src.presentation.serializers.auth import (
    AuthResponseSerializer,
    LoginSerializer,
    RegistroResponseSerializer,
    RegistroSerializer,
)


def _usuario_json(usuario: Usuario) -> dict:
    return {
        "id": str(usuario.id),
        "nombre": usuario.nombre,
        "dni": usuario.dni,
        "telefono": usuario.telefono,
        "email": usuario.email,
        "fotoUrl": usuario.foto_url,
        "rol": usuario.rol.value,
        "isOnline": usuario.is_online,
        "lineaId": usuario.linea_id,
        "lineaNombre": usuario.linea_nombre,
        "subrutaId": usuario.subruta_id,
        "subrutaDbId": usuario.subruta_id,
        "subrutaNombre": usuario.subruta_nombre,
    }


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=LoginSerializer, responses=AuthResponseSerializer)
    def post(self, request):
        datos = LoginSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        usuario = login_use_case().ejecutar(
            datos.validated_data["dni"],
            datos.validated_data["pin"],
        )
        token = generar_token(usuario)
        return Response(
            {
                "exito": True,
                "mensaje": "Inicio de sesión exitoso.",
                "usuario": _usuario_json(usuario),
                "token": token,
            }
        )


class RegistroView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=RegistroSerializer, responses={201: RegistroResponseSerializer})
    def post(self, request):
        datos = RegistroSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        registro_use_case().ejecutar(
            RegistroDTO(
                nombre=datos.validated_data["nombre"],
                dni=datos.validated_data["dni"],
                telefono=datos.validated_data["telefono"],
                email=datos.validated_data["email"],
                pin=datos.validated_data["pin"],
                linea_id=datos.validated_data["lineaId"],
                subruta_id=datos.validated_data.get("subrutaId"),
                rol=datos.validated_data["rol"],
            )
        )
        return Response(
            {
                "exito": True,
                "mensaje": "Solicitud enviada. Un administrador debe aprobarla.",
            },
            status=status.HTTP_201_CREATED,
        )
