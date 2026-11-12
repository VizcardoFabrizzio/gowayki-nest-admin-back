from django.db import IntegrityError

from src.domain.entities.unidad import Unidad
from src.domain.exceptions import ConflictoError
from src.domain.repositories.unidad_repository import UnidadRepository
from src.infrastructure.mappers.unidad_mapper import UnidadMapper
from src.infrastructure.models.unidad import Unidad as UnidadModel


class DjangoUnidadRepository(UnidadRepository):
    def find_all(self) -> list[Unidad]:
        return [UnidadMapper.to_domain(modelo) for modelo in UnidadModel.objects.order_by("id")]

    def find_by_id(self, unidad_id: int) -> Unidad | None:
        modelo = UnidadModel.objects.filter(id=unidad_id).first()
        return UnidadMapper.to_domain(modelo) if modelo else None

    def find_by_linea(self, linea_id: int) -> list[Unidad]:
        return [
            UnidadMapper.to_domain(modelo)
            for modelo in UnidadModel.objects.filter(linea_id=linea_id).order_by("id")
        ]

    def save(self, unidad: Unidad) -> Unidad:
        modelo = UnidadMapper.to_orm(unidad)
        try:
            modelo.save()
        except IntegrityError as exc:
            raise ConflictoError("La placa ya esta registrada o la linea no existe.") from exc
        return UnidadMapper.to_domain(modelo)

    def delete(self, unidad_id: int) -> None:
        try:
            UnidadModel.objects.filter(id=unidad_id).delete()
        except IntegrityError as exc:
            raise ConflictoError(
                "No se puede eliminar la unidad porque tiene registros asociados."
            ) from exc

    def exists_by_id(self, unidad_id: int) -> bool:
        return UnidadModel.objects.filter(id=unidad_id).exists()

    def exists_by_placa(self, placa: str, exclude_id: int | None = None) -> bool:
        consulta = UnidadModel.objects.filter(placa=placa)
        if exclude_id is not None:
            consulta = consulta.exclude(id=exclude_id)
        return consulta.exists()
