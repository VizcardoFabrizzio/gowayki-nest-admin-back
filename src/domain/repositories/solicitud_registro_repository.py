from abc import ABC, abstractmethod

from src.domain.entities.solicitud_registro import SolicitudRegistro


class SolicitudRegistroRepository(ABC):
    @abstractmethod
    def find_all(self) -> list[SolicitudRegistro]:
        pass

    @abstractmethod
    def find_by_id(self, solicitud_id: int) -> SolicitudRegistro | None:
        pass

    @abstractmethod
    def save(self, solicitud: SolicitudRegistro) -> SolicitudRegistro:
        pass

    @abstractmethod
    def find_pendiente_by_dni(self, dni: str) -> SolicitudRegistro | None:
        pass
