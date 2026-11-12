from abc import ABC, abstractmethod

from src.domain.entities.punto_control import PuntoControl


class PuntoControlRepository(ABC):
    @abstractmethod
    def find_by_linea(self, linea_id: int) -> list[PuntoControl]:
        pass
