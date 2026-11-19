from django.db import IntegrityError, connection
from django.db.models import QuerySet
from django.db.models.expressions import RawSQL

from src.domain.entities.unidad import Unidad
from src.domain.exceptions import ConflictoError
from src.domain.repositories.unidad_repository import UnidadRepository
from src.infrastructure.mappers.unidad_mapper import UnidadMapper
from src.infrastructure.models.unidad import Unidad as UnidadModel


class DjangoUnidadRepository(UnidadRepository):
    def _con_posicion(self, consulta: QuerySet) -> QuerySet:
        return consulta.select_related("linea").annotate(
            posicion_lat=RawSQL(
                "(select ST_Y(up.posicion) from unidad_posicion up where up.unidad_id = unidad.id)",
                [],
            ),
            posicion_lng=RawSQL(
                "(select ST_X(up.posicion) from unidad_posicion up where up.unidad_id = unidad.id)",
                [],
            ),
            posicion_velocidad=RawSQL(
                "(select up.velocidad_kmh from unidad_posicion up where up.unidad_id = unidad.id)",
                [],
            ),
            posicion_rumbo=RawSQL(
                "(select up.rumbo_grados from unidad_posicion up where up.unidad_id = unidad.id)",
                [],
            ),
            posicion_actualizada=RawSQL(
                "(select up.updated_at from unidad_posicion up where up.unidad_id = unidad.id)",
                [],
            ),
        )

    def find_all(self) -> list[Unidad]:
        consulta = self._con_posicion(UnidadModel.objects.order_by("id"))
        return [UnidadMapper.to_domain(modelo) for modelo in consulta]

    def find_by_id(self, unidad_id: int) -> Unidad | None:
        modelo = self._con_posicion(UnidadModel.objects.filter(id=unidad_id)).first()
        return UnidadMapper.to_domain(modelo) if modelo else None

    def find_by_linea(self, linea_id: int) -> list[Unidad]:
        consulta = self._con_posicion(UnidadModel.objects.filter(linea_id=linea_id).order_by("id"))
        return [UnidadMapper.to_domain(modelo) for modelo in consulta]

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

    def has_registros(self, unidad_id: int) -> bool:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                select exists(select 1 from asignacion_turno where unidad_id = %s)
                    or exists(select 1 from alerta_incidencia where unidad_id = %s)
                """,
                [unidad_id, unidad_id],
            )
            return bool(cursor.fetchone()[0])
