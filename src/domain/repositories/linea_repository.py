from abc import ABC, abstractmethod

from src.domain.entities.linea import Linea


class LineaRepository(ABC):
    @abstractmethod
    def find_all(self) -> list[Linea]:
        pass

    @abstractmethod
    def find_by_id(self, linea_id: int) -> Linea | None:
        pass

    @abstractmethod
    def save(self, linea: Linea) -> Linea:
        pass

    @abstractmethod
    def delete(self, linea_id: int) -> None:
        pass

    @abstractmethod
    def exists_by_id(self, linea_id: int) -> bool:
        pass

    @abstractmethod
    def has_unidades(self, linea_id: int) -> bool:
        pass
