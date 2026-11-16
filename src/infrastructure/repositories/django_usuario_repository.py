from datetime import datetime
from uuid import UUID

from django.db import IntegrityError

from src.domain.entities.usuario import Usuario
from src.domain.exceptions import ConflictoError
from src.domain.repositories.usuario_repository import CredencialesUsuario, UsuarioRepository
from src.domain.value_objects import Rol
from src.infrastructure.mappers.usuario_mapper import UsuarioMapper
from src.infrastructure.models.linea import Linea as LineaModel
from src.infrastructure.models.usuario import Usuario as UsuarioModel
from src.infrastructure.models.usuario_linea import UsuarioLinea as UsuarioLineaModel


class DjangoUsuarioRepository(UsuarioRepository):
    def find_all(self) -> list[Usuario]:
        modelos = list(UsuarioModel.objects.order_by("nombre"))
        lineas = self._lineas_por_usuario([modelo.id for modelo in modelos])
        usuarios = []
        for modelo in modelos:
            linea_id, linea_nombre = lineas.get(modelo.id, (None, None))
            usuarios.append(UsuarioMapper.to_domain(modelo, linea_id, linea_nombre))
        return usuarios

    def find_by_id(self, usuario_id: UUID) -> Usuario | None:
        modelo = UsuarioModel.objects.filter(id=usuario_id).first()
        return self._to_domain(modelo) if modelo else None

    def find_by_dni(self, dni: str) -> Usuario | None:
        modelo = UsuarioModel.objects.filter(dni=dni).first()
        return self._to_domain(modelo) if modelo else None

    def find_by_email(self, email: str) -> Usuario | None:
        modelo = UsuarioModel.objects.filter(email__iexact=email).first()
        return self._to_domain(modelo) if modelo else None

    def find_auth_by_dni(self, dni: str) -> CredencialesUsuario | None:
        modelo = UsuarioModel.objects.filter(dni=dni).first()
        return self._to_credentials(modelo) if modelo else None

    def find_auth_by_email(self, email: str) -> CredencialesUsuario | None:
        modelo = UsuarioModel.objects.filter(email__iexact=email).first()
        return self._to_credentials(modelo) if modelo else None

    def save(self, usuario: Usuario, pin_hash: str | None = None) -> Usuario:
        modelo = UsuarioMapper.to_orm(usuario)
        datos = {
            "nombre": modelo.nombre,
            "dni": modelo.dni,
            "telefono": modelo.telefono,
            "email": modelo.email,
            "foto_url": modelo.foto_url,
            "rol": modelo.rol,
            "is_online": modelo.is_online,
            "created_at": modelo.created_at,
        }
        if pin_hash is not None:
            datos["pin_hash"] = pin_hash
        try:
            guardado, _ = UsuarioModel.objects.update_or_create(
                id=usuario.id,
                defaults=datos,
            )
        except IntegrityError as exc:
            raise ConflictoError("El DNI, telefono o email ya esta registrado.") from exc
        return self._to_domain(guardado)

    def update_login_state(
        self,
        usuario_id: UUID,
        is_online: bool,
        intentos_fallidos: int,
        bloqueado_hasta: datetime | None,
    ) -> None:
        UsuarioModel.objects.filter(id=usuario_id).update(
            is_online=is_online,
            intentos_fallidos=intentos_fallidos,
            bloqueado_hasta=bloqueado_hasta,
        )

    def delete(self, usuario_id: UUID) -> None:
        try:
            UsuarioModel.objects.filter(id=usuario_id).delete()
        except IntegrityError as exc:
            raise ConflictoError(
                "No se puede eliminar el usuario porque tiene registros asociados."
            ) from exc

    def count_admins(self) -> int:
        return UsuarioModel.objects.filter(rol=Rol.ADMIN.value).count()

    def exists_by_dni(self, dni: str, exclude_id: UUID | None = None) -> bool:
        consulta = UsuarioModel.objects.filter(dni=dni)
        if exclude_id is not None:
            consulta = consulta.exclude(id=exclude_id)
        return consulta.exists()

    def exists_by_telefono(self, telefono: str, exclude_id: UUID | None = None) -> bool:
        consulta = UsuarioModel.objects.filter(telefono=telefono)
        if exclude_id is not None:
            consulta = consulta.exclude(id=exclude_id)
        return consulta.exists()

    def exists_by_email(self, email: str, exclude_id: UUID | None = None) -> bool:
        consulta = UsuarioModel.objects.filter(email__iexact=email)
        if exclude_id is not None:
            consulta = consulta.exclude(id=exclude_id)
        return consulta.exists()

    @classmethod
    def _to_domain(cls, modelo: UsuarioModel) -> Usuario:
        linea_id, linea_nombre = cls._linea_de(modelo.id)
        return UsuarioMapper.to_domain(modelo, linea_id, linea_nombre)

    @staticmethod
    def _linea_de(usuario_id: UUID) -> tuple[int | None, str | None]:
        linea_id = (
            UsuarioLineaModel.objects.filter(usuario_id=usuario_id)
            .values_list("linea_id", flat=True)
            .first()
        )
        if linea_id is None:
            return None, None
        nombre = LineaModel.objects.filter(id=linea_id).values_list("nombre", flat=True).first()
        return linea_id, nombre

    @staticmethod
    def _lineas_por_usuario(ids: list[UUID]) -> dict[UUID, tuple[int | None, str | None]]:
        if not ids:
            return {}
        filas = list(
            UsuarioLineaModel.objects.filter(usuario_id__in=ids).values(
                "usuario_id", "linea_id"
            )
        )
        nombres = dict(
            LineaModel.objects.filter(id__in={fila["linea_id"] for fila in filas}).values_list(
                "id", "nombre"
            )
        )
        return {
            fila["usuario_id"]: (fila["linea_id"], nombres.get(fila["linea_id"]))
            for fila in filas
        }

    @staticmethod
    def _to_credentials(modelo: UsuarioModel) -> CredencialesUsuario:
        return CredencialesUsuario(
            id=modelo.id,
            pin_hash=modelo.pin_hash,
            intentos_fallidos=modelo.intentos_fallidos,
            bloqueado_hasta=modelo.bloqueado_hasta,
        )
