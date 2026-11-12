from django.db import IntegrityError

from src.domain.entities.linea import Linea
from src.domain.exceptions import ConflictoError
from src.domain.repositories.linea_repository import LineaRepository
from src.infrastructure.mappers.linea_mapper import LineaMapper
from src.infrastructure.models.linea import Linea as LineaModel
from src.infrastructure.models.unidad import Unidad as UnidadModel


class DjangoLineaRepository(LineaRepository):
    def find_all(self) -> list[Linea]:
        return [LineaMapper.to_domain(modelo) for modelo in LineaModel.objects.order_by("id")]

    def find_by_id(self, linea_id: int) -> Linea | None:
        modelo = LineaModel.objects.filter(id=linea_id).first()
        return LineaMapper.to_domain(modelo) if modelo else None

    def save(self, linea: Linea) -> Linea:
        modelo = LineaMapper.to_orm(linea)
        modelo.save()
        return LineaMapper.to_domain(modelo)

    def delete(self, linea_id: int) -> None:
        try:
            LineaModel.objects.filter(id=linea_id).delete()
        except IntegrityError as exc:
            raise ConflictoError(
                "No se puede eliminar la linea porque tiene unidades asignadas."
            ) from exc

    def exists_by_id(self, linea_id: int) -> bool:
        return LineaModel.objects.filter(id=linea_id).exists()

    def has_unidades(self, linea_id: int) -> bool:
        return UnidadModel.objects.filter(linea_id=linea_id).exists()
