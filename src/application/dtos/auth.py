from dataclasses import dataclass


@dataclass(frozen=True)
class LoginDTO:
    identificador: str
    pin: str


@dataclass(frozen=True)
class RegistroDTO:
    nombre: str
    dni: str
    telefono: str
    email: str | None
    pin: str
