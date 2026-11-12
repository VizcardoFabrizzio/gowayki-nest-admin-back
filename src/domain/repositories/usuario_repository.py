from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.entities.usuario import Usuario


@dataclass(frozen=True)
class CredencialesUsuario:
    id: UUID
    pin_hash: str
    intentos_fallidos: int
    bloqueado_hasta: datetime | None


class UsuarioRepository(ABC):
    @abstractmethod
    def find_all(self) -> list[Usuario]:
        pass

    @abstractmethod
    def find_by_id(self, usuario_id: UUID) -> Usuario | None:
        pass

    @abstractmethod
    def find_by_dni(self, dni: str) -> Usuario | None:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Usuario | None:
        pass

    @abstractmethod
    def find_auth_by_dni(self, dni: str) -> CredencialesUsuario | None:
        pass

    @abstractmethod
    def find_auth_by_email(self, email: str) -> CredencialesUsuario | None:
        pass

    @abstractmethod
    def save(self, usuario: Usuario, pin_hash: str | None = None) -> Usuario:
        pass

    @abstractmethod
    def update_login_state(
        self,
        usuario_id: UUID,
        is_online: bool,
        intentos_fallidos: int,
        bloqueado_hasta: datetime | None,
    ) -> None:
        pass

    @abstractmethod
    def delete(self, usuario_id: UUID) -> None:
        pass

    @abstractmethod
    def count_admins(self) -> int:
        pass

    @abstractmethod
    def exists_by_dni(self, dni: str, exclude_id: UUID | None = None) -> bool:
        pass

    @abstractmethod
    def exists_by_telefono(self, telefono: str, exclude_id: UUID | None = None) -> bool:
        pass

    @abstractmethod
    def exists_by_email(self, email: str, exclude_id: UUID | None = None) -> bool:
        pass
