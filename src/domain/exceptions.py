class DominioError(Exception):
    pass


class ValidacionError(DominioError):
    pass


class NoEncontradoError(DominioError):
    pass


class ConflictoError(DominioError):
    pass


class NoAutorizadoError(DominioError):
    pass


class CredencialesInvalidasError(NoAutorizadoError):
    pass


class AccesoDenegadoError(NoAutorizadoError):
    pass


class CuentaBloqueadaError(DominioError):
    pass
