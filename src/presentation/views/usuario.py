from uuid import UUID

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from src.application.dtos.usuario import ActualizarRolDTO
from src.domain.entities.usuario import Usuario
from src.infrastructure.container import (
    actualizar_rol_use_case,
    eliminar_usuario_use_case,
    listar_usuarios_use_case,
)
from src.presentation.permissions import EsAdmin
from src.presentation.serializers.usuario import ActualizarRolSerializer, UsuarioSerializer


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
    }


class UsuarioListView(APIView):
    permission_classes = [EsAdmin]

    @extend_schema(responses=UsuarioSerializer(many=True))
    def get(self, request):
        usuarios = listar_usuarios_use_case().ejecutar()
        return Response([_usuario_json(usuario) for usuario in usuarios])


class UsuarioDetailView(APIView):
    permission_classes = [EsAdmin]

    @extend_schema(request=ActualizarRolSerializer, responses=UsuarioSerializer)
    def patch(self, request, usuario_id: UUID):
        datos = ActualizarRolSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        usuario = actualizar_rol_use_case().ejecutar(
            usuario_id,
            ActualizarRolDTO(rol=datos.validated_data["rol"]),
        )
        return Response(_usuario_json(usuario))

    @extend_schema(responses={204: None})
    def delete(self, request, usuario_id: UUID):
        eliminar_usuario_use_case().ejecutar(usuario_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
