from datetime import UTC, datetime

from src.application.dtos.auth import RegistroDTO
from src.domain.entities.solicitud_registro import SolicitudRegistro
from src.domain.exceptions import ConflictoError, ValidacionError
from src.domain.repositories.linea_repository import LineaRepository
from src.domain.repositories.solicitud_registro_repository import SolicitudRegistroRepository
from src.domain.repositories.usuario_repository import UsuarioRepository
from src.domain.value_objects import Dni, EstadoSolicitud, Pin, Rol, Telefono, TipoSolicitud
from src.infrastructure.security.pin_hasher import PinHasher


class RegistroUseCase:
    def __init__(
        self,
        usuarios: UsuarioRepository,
        solicitudes: SolicitudRegistroRepository,
        lineas: LineaRepository,
    ) -> None:
        self._usuarios = usuarios
        self._solicitudes = solicitudes
        self._lineas = lineas

    def ejecutar(self, datos: RegistroDTO) -> SolicitudRegistro:
        nombre = (datos.nombre or "").strip()
        if not nombre:
            raise ValidacionError("El nombre es obligatorio.")

        rol = (datos.rol or Rol.JEFE_RUTA.value).strip().upper()
        if rol != Rol.JEFE_RUTA.value:
            raise ValidacionError("El registro público solo admite jefes de ruta.")

        dni = Dni(datos.dni or "")
        telefono = Telefono(datos.telefono or "")
        pin = Pin(datos.pin or "")
        email = self._normalizar_email(datos.email)

        if datos.linea_id is None:
            raise ValidacionError("Debes seleccionar una ruta.")
        linea = self._lineas.find_by_id(datos.linea_id)
        if linea is None:
            raise ValidacionError("La ruta seleccionada no existe.")

        if self._usuarios.exists_by_dni(str(dni)) or self._solicitudes.find_pendiente_by_dni(
            str(dni)
        ):
            raise ConflictoError("Ya existe una cuenta o solicitud con ese DNI.")
        if self._usuarios.exists_by_telefono(str(telefono)):
            raise ConflictoError("El teléfono ya está registrado.")
        if email and self._usuarios.exists_by_email(email):
            raise ConflictoError("El email ya está registrado.")

        solicitud = SolicitudRegistro(
            id=None,
            tipo=TipoSolicitud.JEFE_RUTA,
            dni=str(dni),
            nombre_completo=nombre,
            telefono=str(telefono),
            email=email,
            ruta_trabajo=linea.nombre,
            linea_solicitada_id=linea.id,
            pin_hash=PinHasher.hash(str(pin)),
            estado=EstadoSolicitud.PENDIENTE,
            creado_en=datetime.now(UTC),
        )
        return self._solicitudes.save(solicitud)

    @staticmethod
    def _normalizar_email(valor: str | None) -> str | None:
        email = (valor or "").strip().lower()
        if not email:
            return None
        dominio = email.split("@")[-1]
        if "@" not in email or "." not in dominio:
            raise ValidacionError("El email no es válido.")
        return email
