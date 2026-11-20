from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ListarSolicitudesDTO:
    rol: str = ""
    linea_id: int | None = None


@dataclass(frozen=True)
class CrearCambioRutaDTO:
    tipo: str = "CAMBIO_RUTA"
    usuario_id: UUID | None = None
    linea_solicitada_id: int | None = None


@dataclass(frozen=True)
class ResolverSolicitudDTO:
    estado: str = ""
    usuario_asignado: str | None = None
