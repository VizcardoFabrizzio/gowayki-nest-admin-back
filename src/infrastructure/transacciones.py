from contextlib import AbstractContextManager

from django.db import transaction

from src.domain.transacciones import GestorTransacciones


class TransaccionesDjango(GestorTransacciones):
    def atomic(self) -> AbstractContextManager[None]:
        return transaction.atomic()
