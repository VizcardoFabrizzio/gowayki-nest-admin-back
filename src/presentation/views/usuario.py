from uuid import UUID

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from src.application.dtos.usuario import ActualizarRolDTO, ActualizarSubrutaDTO
from src.domain.entities.usuario import Usuario
from src.infrastructure.container import (
    actualizar_rol_use_case,
    actualizar_subruta_use_case,
    eliminar_usuario_use_case,
    listar_usuarios_use_case,
)
from src.presentation.permissions import EsAdmin, EsAdminOJefeRuta
from src.presentation.serializers.usuario import (
    ActualizarRolSerializer,
    ActualizarSubrutaSerializer,
    UsuarioSerializer,
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


class UsuarioListView(APIView):
    permission_classes = [EsAdmin]

    # "Mis choferes" necesita el catálogo de usuarios de la línea del jefe.
    # El administrador sigue viendo todos; el resto de métodos siguen siendo
    # exclusivos de ADMIN.
    def get_permissions(self):
        if self.request.method == "GET":
            return [EsAdminOJefeRuta()]
        return super().get_permissions()

    @extend_schema(responses=UsuarioSerializer(many=True))
    def get(self, request):
        usuarios = listar_usuarios_use_case().ejecutar()
        if getattr(request.user, "rol", None) != "ADMIN":
            linea_id = getattr(request.user, "linea_id", None)
            usuarios = [u for u in usuarios if u.linea_id == linea_id]
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


class UsuarioSubrutaView(APIView):
    permission_classes = [EsAdminOJefeRuta]

    @extend_schema(request=ActualizarSubrutaSerializer, responses=UsuarioSerializer)
    def patch(self, request, usuario_id: UUID):
        # Un jefe puede cambiar solo SU subruta; el admin puede cambiar
        # la de cualquier cuenta, igual que con el resto de endpoints.
        usuario_autenticado = request.user
        if getattr(usuario_autenticado, "rol", None) != "ADMIN" and str(
            getattr(usuario_autenticado, "id", "")
        ) != str(usuario_id):
            raise PermissionDenied("Solo puedes cambiar tu propia subruta.")

        datos = ActualizarSubrutaSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        usuario = actualizar_subruta_use_case().ejecutar(
            usuario_id,
            ActualizarSubrutaDTO(subruta_id=datos.validated_data["subrutaId"]),
        )
        return Response(_usuario_json(usuario))
