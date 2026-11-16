from abc import ABC, abstractmethod

from src.domain.entities.solicitud_registro import SolicitudRegistro


class SolicitudRegistroRepository(ABC):
    @abstractmethod
    def save(self, solicitud: SolicitudRegistro) -> SolicitudRegistro:
        pass

    @abstractmethod
    def find_pendiente_by_dni(self, dni: str) -> SolicitudRegistro | None:
        pass
