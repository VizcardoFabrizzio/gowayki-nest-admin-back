from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.entities.linea import Linea
from src.domain.entities.punto_control import PuntoControl
from src.domain.entities.solicitud_registro import SolicitudRegistro
from src.domain.entities.unidad import Unidad
from src.domain.entities.usuario import Usuario
from src.domain.exceptions import ConflictoError
from src.domain.repositories.linea_repository import LineaRepository
from src.domain.repositories.punto_control_repository import PuntoControlRepository
from src.domain.repositories.solicitud_registro_repository import (
    SolicitudRegistroRepository,
)
from src.domain.repositories.unidad_repository import UnidadRepository
from src.domain.repositories.usuario_repository import (
    CredencialesUsuario,
    UsuarioRepository,
)
from src.domain.value_objects import Rol


@dataclass
class Repos:
    usuarios: "FakeUsuarioRepository"
    lineas: "FakeLineaRepository"
    unidades: "FakeUnidadRepository"
    puntos: "FakePuntoControlRepository"
    solicitudes: "FakeSolicitudRegistroRepository"


def make_repos() -> Repos:
    lineas = FakeLineaRepository()
    unidades = FakeUnidadRepository(lineas)
    usuarios = FakeUsuarioRepository(lineas)
    puntos = FakePuntoControlRepository(lineas)
    solicitudes = FakeSolicitudRegistroRepository()
    return Repos(
        usuarios=usuarios,
        lineas=lineas,
        unidades=unidades,
        puntos=puntos,
        solicitudes=solicitudes,
    )


class FakeLineaRepository(LineaRepository):
    def __init__(self) -> None:
        self._items: dict[int, Linea] = {}
        self._next = 1

    def find_all(self) -> list[Linea]:
        return sorted(self._items.values(), key=lambda x: x.id or 0)

    def find_by_id(self, linea_id: int) -> Linea | None:
        return self._items.get(linea_id)

    def save(self, linea: Linea) -> Linea:
        if linea.id is None:
            linea = Linea(
                id=self._next,
                nombre=linea.nombre,
                origen=linea.origen,
                destino=linea.destino,
                corredor=linea.corredor,
                color_hex=linea.color_hex,
                created_at=linea.created_at,
            )
            self._next += 1
        self._items[linea.id] = linea
        return linea

    def delete(self, linea_id: int) -> None:
        self._items.pop(linea_id, None)

    def exists_by_id(self, linea_id: int) -> bool:
        return linea_id in self._items

    def has_unidades(self, linea_id: int) -> bool:
        # resolved by unidades repo; default False here
        return False


class FakeUnidadRepository(UnidadRepository):
    def __init__(self, lineas: FakeLineaRepository) -> None:
        self._items: dict[int, Unidad] = {}
        self._next = 1
        self._lineas = lineas
        self._registros: set[int] = set()

    def set_has_registros(self, unidad_id: int, value: bool = True) -> None:
        if value:
            self._registros.add(unidad_id)
        else:
            self._registros.discard(unidad_id)

    def find_all(self) -> list[Unidad]:
        return list(self._items.values())

    def find_by_id(self, unidad_id: int) -> Unidad | None:
        return self._items.get(unidad_id)

    def find_by_linea(self, linea_id: int) -> list[Unidad]:
        return [u for u in self._items.values() if u.linea_id == linea_id]

    def save(self, unidad: Unidad) -> Unidad:
        if unidad.id is None:
            unidad = Unidad(
                id=self._next,
                numero_padron=unidad.numero_padron,
                placa=unidad.placa,
                linea_id=unidad.linea_id,
                estado=unidad.estado,
                created_at=unidad.created_at,
                linea_nombre=unidad.linea_nombre,
                posicion_actual=unidad.posicion_actual,
            )
            self._next += 1
        # refresh linea_nombre
        linea = self._lineas.find_by_id(unidad.linea_id)
        if linea is not None:
            unidad = Unidad(
                id=unidad.id,
                numero_padron=unidad.numero_padron,
                placa=unidad.placa,
                linea_id=unidad.linea_id,
                estado=unidad.estado,
                created_at=unidad.created_at,
                linea_nombre=linea.nombre,
                posicion_actual=unidad.posicion_actual,
            )
        self._items[unidad.id] = unidad
        return unidad

    def delete(self, unidad_id: int) -> None:
        self._items.pop(unidad_id, None)

    def exists_by_id(self, unidad_id: int) -> bool:
        return unidad_id in self._items

    def exists_by_placa(self, placa: str, exclude_id: int | None = None) -> bool:
        for uid, u in self._items.items():
            if uid == exclude_id:
                continue
            if u.placa == placa:
                return True
        return False

    def has_registros(self, unidad_id: int) -> bool:
        return unidad_id in self._registros


class FakePuntoControlRepository(PuntoControlRepository):
    def __init__(self, lineas: FakeLineaRepository) -> None:
        self._items: dict[int, list[PuntoControl]] = {}
        self._lineas = lineas

    def seed(self, linea_id: int, puntos: list[PuntoControl]) -> None:
        self._items[linea_id] = list(puntos)

    def find_by_linea(self, linea_id: int) -> list[PuntoControl]:
        return list(self._items.get(linea_id, []))


class FakeSolicitudRegistroRepository(SolicitudRegistroRepository):
    def __init__(self) -> None:
        self._items: list[SolicitudRegistro] = []
        self._next = 1

    def find_all(self) -> list[SolicitudRegistro]:
        return list(self._items)

    def find_by_id(self, solicitud_id: int) -> SolicitudRegistro | None:
        for s in self._items:
            if s.id == solicitud_id:
                return s
        return None

    def save(self, solicitud: SolicitudRegistro) -> SolicitudRegistro:
        if solicitud.id is None:
            solicitud = SolicitudRegistro(
                id=self._next,
                tipo=solicitud.tipo,
                dni=solicitud.dni,
                nombre_completo=solicitud.nombre_completo,
                estado=solicitud.estado,
                creado_en=solicitud.creado_en,
                telefono=solicitud.telefono,
                email=solicitud.email,
                ruta_trabajo=solicitud.ruta_trabajo,
                placa_numero=solicitud.placa_numero,
                linea_solicitada_id=solicitud.linea_solicitada_id,
                usuario_id=solicitud.usuario_id,
                pin_hash=solicitud.pin_hash,
                usuario_asignado=solicitud.usuario_asignado,
                actualizado_en=solicitud.actualizado_en,
            )
            self._next += 1
            self._items.append(solicitud)
            return solicitud
        # update existing
        for i, s in enumerate(self._items):
            if s.id == solicitud.id:
                self._items[i] = solicitud
                return solicitud
        self._items.append(solicitud)
        return solicitud

    def find_pendiente_by_dni(self, dni: str) -> SolicitudRegistro | None:
        for s in self._items:
            if s.dni == dni and s.estado.value == "PENDIENTE":
                return s
        return None


class FakeUsuarioRepository(UsuarioRepository):
    def __init__(self, lineas: FakeLineaRepository) -> None:
        self._items: dict[UUID, Usuario] = {}
        self._auth: dict[UUID, CredencialesUsuario] = {}
        self._lineas_rel: dict[UUID, int | None] = {}
        self._lineas = lineas

    def _linea_info(self, usuario_id: UUID) -> tuple[int | None, str | None]:
        linea_id = self._lineas_rel.get(usuario_id)
        if linea_id is None:
            return None, None
        linea = self._lineas.find_by_id(linea_id)
        return linea_id, (linea.nombre if linea else None)

    def _to_domain(self, usuario: Usuario) -> Usuario:
        linea_id, linea_nombre = self._linea_info(usuario.id)
        # rebuild with linea info
        return Usuario(
            id=usuario.id,
            nombre=usuario.nombre,
            dni=usuario.dni,
            telefono=usuario.telefono,
            email=usuario.email,
            foto_url=usuario.foto_url,
            rol=usuario.rol,
            is_online=usuario.is_online,
            created_at=usuario.created_at,
            linea_id=linea_id,
            linea_nombre=linea_nombre,
        )

    def find_all(self) -> list[Usuario]:
        out = []
        for u in self._items.values():
            out.append(self._to_domain(u))
        out.sort(key=lambda x: x.nombre)
        return out

    def find_by_id(self, usuario_id: UUID) -> Usuario | None:
        u = self._items.get(usuario_id)
        return self._to_domain(u) if u else None

    def find_by_dni(self, dni: str) -> Usuario | None:
        for u in self._items.values():
            if u.dni == dni:
                return self._to_domain(u)
        return None

    def find_by_email(self, email: str) -> Usuario | None:
        for u in self._items.values():
            if u.email is not None and u.email.lower() == email.lower():
                return self._to_domain(u)
        return None

    def find_auth_by_dni(self, dni: str) -> CredencialesUsuario | None:
        for uid, u in self._items.items():
            if u.dni == dni:
                return self._auth.get(uid)
        return None

    def find_auth_by_email(self, email: str) -> CredencialesUsuario | None:
        for uid, u in self._items.items():
            if u.email is not None and u.email.lower() == email.lower():
                return self._auth.get(uid)
        return None

    def save(
        self,
        usuario: Usuario,
        pin_hash: str | None = None,
        linea_id: int | None = None,
    ) -> Usuario:
        # conflict checks for new-ish: check dni/telefono/email excluding self
        for uid, u in self._items.items():
            if uid == usuario.id:
                continue
            if u.dni == usuario.dni:
                raise ConflictoError("dup dni")
            if u.telefono == usuario.telefono:
                raise ConflictoError("dup tel")
            if usuario.email and u.email and u.email.lower() == usuario.email.lower():
                raise ConflictoError("dup email")
        self._items[usuario.id] = usuario
        if pin_hash is not None:
            prev = self._auth.get(usuario.id)
            intentos = prev.intentos_fallidos if prev else 0
            bloqueado = prev.bloqueado_hasta if prev else None
            self._auth[usuario.id] = CredencialesUsuario(
                id=usuario.id,
                pin_hash=pin_hash,
                intentos_fallidos=intentos,
                bloqueado_hasta=bloqueado,
            )
        elif usuario.id not in self._auth:
            # keep existing; if none, set empty? Use provided pin_hash only
            pass
        if linea_id is not None:
            self._lineas_rel[usuario.id] = linea_id
        # if usuario has linea_id attribute? entity has linea_id; but save uses param
        return self._to_domain(usuario)

    def update_login_state(
        self,
        usuario_id: UUID,
        is_online: bool,
        intentos_fallidos: int,
        bloqueado_hasta: datetime | None,
    ) -> None:
        u = self._items.get(usuario_id)
        if u is not None:
            self._items[usuario_id] = Usuario(
                id=u.id,
                nombre=u.nombre,
                dni=u.dni,
                telefono=u.telefono,
                email=u.email,
                foto_url=u.foto_url,
                rol=u.rol,
                is_online=is_online,
                created_at=u.created_at,
                linea_id=u.linea_id,
                linea_nombre=u.linea_nombre,
            )
        if usuario_id in self._auth:
            prev = self._auth[usuario_id]
            self._auth[usuario_id] = CredencialesUsuario(
                id=prev.id,
                pin_hash=prev.pin_hash,
                intentos_fallidos=intentos_fallidos,
                bloqueado_hasta=bloqueado_hasta,
            )

    def delete(self, usuario_id: UUID) -> None:
        self._items.pop(usuario_id, None)
        self._auth.pop(usuario_id, None)
        self._lineas_rel.pop(usuario_id, None)

    def count_admins(self) -> int:
        return sum(1 for u in self._items.values() if u.rol == Rol.ADMIN)

    def exists_by_dni(self, dni: str, exclude_id: UUID | None = None) -> bool:
        for uid, u in self._items.items():
            if exclude_id is not None and uid == exclude_id:
                continue
            if u.dni == dni:
                return True
        return False

    def exists_by_telefono(self, telefono: str, exclude_id: UUID | None = None) -> bool:
        for uid, u in self._items.items():
            if exclude_id is not None and uid == exclude_id:
                continue
            if u.telefono == telefono:
                return True
        return False

    def exists_by_email(self, email: str, exclude_id: UUID | None = None) -> bool:
        for uid, u in self._items.items():
            if exclude_id is not None and uid == exclude_id:
                continue
            if u.email is not None and u.email.lower() == email.lower():
                return True
        return False

    # helper for tests to seed auth
    def seed(self, usuario: Usuario, pin_hash: str, linea_id: int | None = None) -> None:
        self._items[usuario.id] = usuario
        self._auth[usuario.id] = CredencialesUsuario(
            id=usuario.id,
            pin_hash=pin_hash,
            intentos_fallidos=0,
            bloqueado_hasta=None,
        )
        if linea_id is not None:
            self._lineas_rel[usuario.id] = linea_id


# wire has_unidades to use unidades repo
def wire(repos: Repos) -> Repos:
    repos.lineas.has_unidades = lambda lid: any(  # type: ignore
        u.linea_id == lid for u in repos.unidades._items.values()
    )
    return repos
