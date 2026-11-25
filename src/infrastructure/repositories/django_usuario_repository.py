from datetime import UTC, datetime
from uuid import UUID

from django.db import IntegrityError
from django.db.models import F

from src.domain.entities.usuario import Usuario
from src.domain.exceptions import ConflictoError
from src.domain.repositories.usuario_repository import CredencialesUsuario, UsuarioRepository
from src.domain.value_objects import Rol
from src.infrastructure.mappers.usuario_mapper import UsuarioMapper
from src.infrastructure.models.linea import Linea as LineaModel
from src.infrastructure.models.subruta import Subruta as SubrutaModel
from src.infrastructure.models.usuario import Usuario as UsuarioModel
from src.infrastructure.models.usuario_linea import UsuarioLinea as UsuarioLineaModel
from src.infrastructure.repositories.django_subruta_repository import pertenece_a_linea


class DjangoUsuarioRepository(UsuarioRepository):
    def find_all(self) -> list[Usuario]:
        modelos = list(UsuarioModel.objects.filter(activo=True).order_by("nombre"))
        lineas = self._lineas_por_usuario([modelo.id for modelo in modelos])
        usuarios = []
        for modelo in modelos:
            linea_id, linea_nombre, subruta_id, subruta_nombre = lineas.get(
                modelo.id, (None, None, None, None)
            )
            usuarios.append(
                UsuarioMapper.to_domain(modelo, linea_id, linea_nombre, subruta_id, subruta_nombre)
            )
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

    def save(
        self,
        usuario: Usuario,
        pin_hash: str | None = None,
        linea_id: int | None = None,
        subruta_id: int | None = None,
    ) -> Usuario:
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
            "activo": modelo.activo,
            "eliminado_en": modelo.eliminado_en,
            "reactivado_en": modelo.reactivado_en,
        }
        if pin_hash is not None:
            datos["pin_hash"] = pin_hash
        try:
            guardado, _ = UsuarioModel.objects.update_or_create(
                id=usuario.id,
                defaults=datos,
            )
            if linea_id is not None:
                defaults = {"linea_id": linea_id}
                if subruta_id is not None:
                    defaults["subruta_id"] = subruta_id
                UsuarioLineaModel.objects.update_or_create(
                    usuario_id=usuario.id,
                    defaults=defaults,
                )
        except IntegrityError as exc:
            raise ConflictoError(
                "El DNI, telefono o email ya esta registrado, o la linea no existe."
            ) from exc
        return self._to_domain(guardado)

    def asignar_subruta(self, usuario_id: UUID, subruta_id: int) -> Usuario | None:
        fila = UsuarioLineaModel.objects.filter(usuario_id=usuario_id).first()
        if fila is None:
            return None
        subruta = SubrutaModel.objects.filter(id=subruta_id, activa=True).first()
        if subruta is None:
            raise ConflictoError("La subruta no existe o no está activa.")
        linea = LineaModel.objects.filter(id=fila.linea_id).first()
        if linea is None or not pertenece_a_linea(subruta, linea):
            raise ConflictoError("La subruta no pertenece a la línea del jefe.")
        fila.subruta_id = subruta_id
        fila.save(update_fields=["subruta_id"])
        modelo = UsuarioModel.objects.filter(id=usuario_id).first()
        return self._to_domain(modelo) if modelo else None

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

    def desactivar(self, usuario_id: UUID) -> None:
        UsuarioModel.objects.filter(id=usuario_id).update(
            activo=False,
            is_online=False,
            eliminado_en=datetime.now(UTC),
            token_version=F("token_version") + 1,
        )

    def count_admins(self) -> int:
        return UsuarioModel.objects.filter(rol=Rol.ADMIN.value, activo=True).count()

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
        linea_id, linea_nombre, subruta_id, subruta_nombre = cls._linea_de(modelo.id)
        return UsuarioMapper.to_domain(modelo, linea_id, linea_nombre, subruta_id, subruta_nombre)

    @staticmethod
    def _linea_de(
        usuario_id: UUID,
    ) -> tuple[int | None, str | None, int | None, str | None]:
        fila = (
            UsuarioLineaModel.objects.filter(usuario_id=usuario_id)
            .values("linea_id", "subruta_id")
            .first()
        )
        if fila is None:
            return None, None, None, None
        linea_id = fila.get("linea_id")
        nombre = (
            LineaModel.objects.filter(id=linea_id).values_list("nombre", flat=True).first()
            if linea_id is not None
            else None
        )
        subruta_id = fila.get("subruta_id")
        subruta_nombre = (
            SubrutaModel.objects.filter(id=subruta_id).values_list("nombre", flat=True).first()
            if subruta_id is not None
            else None
        )
        return linea_id, nombre, subruta_id, subruta_nombre

    @staticmethod
    def _lineas_por_usuario(
        ids: list[UUID],
    ) -> dict[UUID, tuple[int | None, str | None, int | None, str | None]]:
        if not ids:
            return {}
        filas = list(
            UsuarioLineaModel.objects.filter(usuario_id__in=ids).values(
                "usuario_id", "linea_id", "subruta_id"
            )
        )
        nombres = dict(
            LineaModel.objects.filter(id__in={f["linea_id"] for f in filas}).values_list(
                "id", "nombre"
            )
        )
        subrutas = dict(
            SubrutaModel.objects.filter(
                id__in={f["subruta_id"] for f in filas if f["subruta_id"]}
            ).values_list("id", "nombre")
        )
        return {
            fila["usuario_id"]: (
                fila["linea_id"],
                nombres.get(fila["linea_id"]),
                fila["subruta_id"],
                subrutas.get(fila["subruta_id"]),
            )
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
