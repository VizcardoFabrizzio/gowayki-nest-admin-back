from src.domain.entities.usuario import Usuario
from src.domain.value_objects import Rol
from src.infrastructure.models.usuario import Usuario as UsuarioModel


class UsuarioMapper:
    @staticmethod
    def to_domain(modelo: UsuarioModel) -> Usuario:
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
        )
