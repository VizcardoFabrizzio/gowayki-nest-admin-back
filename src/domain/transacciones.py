from abc import ABC, abstractmethod
from contextlib import AbstractContextManager


class GestorTransacciones(ABC):
    """Puerto de infraestructura para agrupar escrituras en una transacción."""

    @abstractmethod
    def atomic(self) -> AbstractContextManager[None]:
        pass
