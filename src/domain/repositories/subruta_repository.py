from abc import ABC, abstractmethod

from src.domain.entities.subruta import Subruta


class SubrutaRepository(ABC):
    @abstractmethod
    def find_by_id(self, subruta_id: int) -> Subruta | None:
        pass

    @abstractmethod
    def find_activa_de_linea(self, subruta_id: int, linea_id: int) -> Subruta | None:
        """Devuelve la subruta si existe, está activa y pertenece a la línea."""
        pass

    @abstractmethod
    def find_codigos(self, subruta_ids: list[int]) -> dict[int, str]:
        """Códigos de las subrutas indicadas, para enriquecer las respuestas."""
        pass
