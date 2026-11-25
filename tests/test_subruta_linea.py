from src.infrastructure.models.linea import Linea
from src.infrastructure.models.subruta import Subruta
from src.infrastructure.repositories.django_subruta_repository import pertenece_a_linea


def test_la_subruta_pertenece_por_nombre_cuando_la_linea_no_lleva_codigo():
    linea = Linea(id=8, nombre="Emarsistran")
    subruta = Subruta(
        id=355,
        codigo="SB-17654231",
        nombre="Socabaya: B: Horacio Zevallos → Pachacutec",
        linea_codigo="C9",
        linea_nombre="Emarsistran",
        activa=True,
    )
    assert pertenece_a_linea(subruta, linea)


def test_la_subruta_no_pertenece_a_otra_linea():
    linea = Linea(id=1, nombre="Cono Norte")
    subruta = Subruta(
        id=355,
        codigo="SB-17654231",
        nombre="Socabaya: B: Horacio Zevallos → Pachacutec",
        linea_codigo="C9",
        linea_nombre="Emarsistran",
        activa=True,
    )
    assert not pertenece_a_linea(subruta, linea)
