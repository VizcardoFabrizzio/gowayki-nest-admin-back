from src.domain.entities.subruta import Subruta
from src.domain.repositories.subruta_repository import SubrutaRepository
from src.domain.servicios.codigo_linea import codigo_de_linea
from src.infrastructure.models.linea import Linea as LineaModel
from src.infrastructure.models.subruta import Subruta as SubrutaModel


def _normalizar(texto: str | None) -> str:
    import unicodedata

    return unicodedata.normalize("NFD", (texto or "").strip().lower()).encode(
        "ascii", "ignore"
    ).decode().strip()


def pertenece_a_linea(subruta: SubrutaModel, linea: LineaModel) -> bool:
    """La BD compartida guarda el código y el nombre de la línea en la subruta.

    Las líneas del panel no siempre traen el código en el nombre (p. ej.
    'Emarsistran' en vez de 'C9 Emarsistran'), por eso se compara también
    por nombre.
    """
    codigo = codigo_de_linea(linea.nombre)
    if (
        subruta.linea_codigo
        and codigo[:1].upper() == "C"
        and codigo[1:].isdigit()
        and subruta.linea_codigo.strip().upper() == codigo.upper()
    ):
        return True
    nombre_linea = _normalizar(linea.nombre)
    nombre_subruta = _normalizar(getattr(subruta, "linea_nombre", None))
    return bool(
        nombre_linea
        and nombre_subruta
        and (nombre_linea == nombre_subruta or nombre_linea in nombre_subruta or nombre_subruta in nombre_linea)
    )


class DjangoSubrutaRepository(SubrutaRepository):
    @staticmethod
    def _to_domain(modelo: SubrutaModel) -> Subruta:
        return Subruta(
            id=modelo.id,
            codigo=modelo.codigo,
            nombre=modelo.nombre,
            linea_codigo=modelo.linea_codigo,
            activa=modelo.activa,
        )

    def find_by_id(self, subruta_id: int) -> Subruta | None:
        modelo = SubrutaModel.objects.filter(id=subruta_id).first()
        return self._to_domain(modelo) if modelo else None

    def find_activa_de_linea(self, subruta_id: int, linea_id: int) -> Subruta | None:
        subruta = SubrutaModel.objects.filter(id=subruta_id, activa=True).first()
        linea = LineaModel.objects.filter(id=linea_id).first()
        if subruta is None or linea is None or not pertenece_a_linea(subruta, linea):
            return None
        return self._to_domain(subruta)

    def find_codigos(self, subruta_ids: list[int]) -> dict[int, str]:
        if not subruta_ids:
            return {}
        return dict(SubrutaModel.objects.filter(id__in=subruta_ids).values_list("id", "codigo"))
