from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from src.domain.exceptions import (
    AccesoDenegadoError,
    ConflictoError,
    CuentaBloqueadaError,
    DominioError,
    NoAutorizadoError,
    NoEncontradoError,
    ValidacionError,
)


def _texto(data) -> str:
    if isinstance(data, dict):
        if "mensaje" in data:
            return str(data["mensaje"])
        if "detail" in data:
            return str(data["detail"])

        partes = []
        for campo, errores in data.items():
            if isinstance(errores, list | tuple):
                texto = " ".join(str(error) for error in errores)
            else:
                texto = str(errores)
            partes.append(f"{campo}: {texto}")
        return " ".join(partes) if partes else "Error en la solicitud."

    if isinstance(data, list | tuple):
        return " ".join(str(error) for error in data)

    return str(data)


def _estado(exc: DominioError) -> int:
    if isinstance(exc, CuentaBloqueadaError):
        return status.HTTP_423_LOCKED
    if isinstance(exc, AccesoDenegadoError):
        return status.HTTP_403_FORBIDDEN
    if isinstance(exc, ValidacionError):
        return status.HTTP_400_BAD_REQUEST
    if isinstance(exc, NoAutorizadoError):
        return status.HTTP_401_UNAUTHORIZED
    if isinstance(exc, NoEncontradoError):
        return status.HTTP_404_NOT_FOUND
    if isinstance(exc, ConflictoError):
        return status.HTTP_409_CONFLICT
    return status.HTTP_400_BAD_REQUEST


def exception_handler(exc, context):
    if isinstance(exc, DominioError):
        return Response(
            {"exito": False, "mensaje": str(exc)},
            status=_estado(exc),
        )

    response = drf_exception_handler(exc, context)
    if response is None:
        return None

    response.data = {"exito": False, "mensaje": _texto(response.data)}
    return response
