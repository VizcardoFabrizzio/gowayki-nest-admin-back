from src.domain.entities.usuario import Usuario
from src.domain.value_objects import Rol
from src.infrastructure.models.usuario import Usuario as UsuarioModel


class UsuarioMapper:
    @staticmethod
    def to_domain(
        modelo: UsuarioModel,
        linea_id: int | None = None,
        linea_nombre: str | None = None,
        subruta_id: int | None = None,
        subruta_nombre: str | None = None,
    ) -> Usuario:
        return Usuario(
            id=modelo.id,
            nombre=modelo.nombre,
            dni=modelo.dni,
            telefono=modelo.telefono,
            email=modelo.email,
            foto_url=modelo.foto_url,
            rol=Rol(modelo.rol),
            is_online=modelo.is_online,
            created_at=modelo.created_at,
            linea_id=linea_id,
            linea_nombre=linea_nombre,
            subruta_id=subruta_id,
            subruta_nombre=subruta_nombre,
            activo=modelo.activo,
            token_version=modelo.token_version,
            eliminado_en=modelo.eliminado_en,
            reactivado_en=modelo.reactivado_en,
        )

    @staticmethod
    def to_orm(usuario: Usuario) -> UsuarioModel:
        return UsuarioModel(
            id=usuario.id,
            nombre=usuario.nombre,
            dni=usuario.dni,
            telefono=usuario.telefono,
            email=usuario.email,
            foto_url=usuario.foto_url,
            rol=usuario.rol.value,
            is_online=usuario.is_online,
            created_at=usuario.created_at,
            activo=usuario.activo,
            eliminado_en=usuario.eliminado_en,
            reactivado_en=usuario.reactivado_en,
        )
