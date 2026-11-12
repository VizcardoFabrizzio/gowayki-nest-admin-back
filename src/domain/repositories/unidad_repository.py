from abc import ABC, abstractmethod

from src.domain.entities.unidad import Unidad


class UnidadRepository(ABC):
    @abstractmethod
    def find_all(self) -> list[Unidad]:
        pass

    @abstractmethod
    def find_by_id(self, unidad_id: int) -> Unidad | None:
        pass

    @abstractmethod
    def find_by_linea(self, linea_id: int) -> list[Unidad]:
        pass

    @abstractmethod
    def save(self, unidad: Unidad) -> Unidad:
        pass

    @abstractmethod
    def delete(self, unidad_id: int) -> None:
        pass

    @abstractmethod
    def exists_by_id(self, unidad_id: int) -> bool:
        pass

    @abstractmethod
    def exists_by_placa(self, placa: str, exclude_id: int | None = None) -> bool:
        pass
