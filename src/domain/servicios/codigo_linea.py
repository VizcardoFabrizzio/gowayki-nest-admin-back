import re


def codigo_de_linea(nombre: str | None) -> str:
    """Extrae el código de la línea desde su nombre (p. ej. 'C2 Terminal' -> 'C2')."""
    texto = re.sub(r"\s+", " ", (nombre or "").strip().upper())
    coincidencia = re.match(r"^([A-Z]+\s*\d+)", texto)
    if coincidencia:
        return re.sub(r"\s+", "", coincidencia.group(1))
    return re.sub(r"\s+", "", texto)
