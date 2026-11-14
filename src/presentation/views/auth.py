from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from src.application.dtos.auth import RegistroDTO
from src.domain.entities.usuario import Usuario
from src.infrastructure.container import login_use_case, registro_use_case
from src.presentation.serializers.auth import (
    AuthResponseSerializer,
    LoginSerializer,
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
    }


class LoginView(APIView):
    @extend_schema(request=LoginSerializer, responses=AuthResponseSerializer)
    def post(self, request):
        datos = LoginSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        usuario = login_use_case().ejecutar(
            datos.validated_data["dni"],
            datos.validated_data["pin"],
        )
        return Response(
            {
                "exito": True,
                "mensaje": "Inicio de sesión exitoso.",
                "usuario": _usuario_json(usuario),
            }
        )


class RegistroView(APIView):
    @extend_schema(request=RegistroSerializer, responses={201: AuthResponseSerializer})
    def post(self, request):
        datos = RegistroSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        usuario = registro_use_case().ejecutar(
            RegistroDTO(
                nombre=datos.validated_data["nombre"],
                dni=datos.validated_data["dni"],
                telefono=datos.validated_data["telefono"],
                email=datos.validated_data["email"],
                pin=datos.validated_data["pin"],
            )
        )
        return Response(
            {
                "exito": True,
                "mensaje": "Cuenta creada correctamente.",
                "usuario": _usuario_json(usuario),
            },
            status=status.HTTP_201_CREATED,
        )
