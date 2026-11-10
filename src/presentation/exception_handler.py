from rest_framework.views import exception_handler as drf_exception_handler


def _texto(data) -> str:
    if isinstance(data, dict):
        if "mensaje" in data:
            return str(data["mensaje"])
        if "detail" in data:
            return str(data["detail"])

        partes = []
        for campo, errores in data.items():
            if isinstance(errores, (list, tuple)):
                texto = " ".join(str(error) for error in errores)
            else:
                texto = str(errores)
            partes.append(f"{campo}: {texto}")
        return " ".join(partes) if partes else "Error en la solicitud."

    if isinstance(data, (list, tuple)):
        return " ".join(str(error) for error in data)

    return str(data)


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is None:
        return None

    response.data = {"exito": False, "mensaje": _texto(response.data)}
    return response
