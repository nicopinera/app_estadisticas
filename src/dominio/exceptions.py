"""Excepciones de dominio para la aplicacion de estadisticas."""


class ErrorDeDominio(Exception):
    """Clase base para todas las excepciones de dominio."""

    pass


class DNIDuplicadoError(ErrorDeDominio):
    """Se lanza cuando se intenta guardar un jugador con un DNI ya registrado."""

    pass


class ClubNoEncontradoError(ErrorDeDominio):
    """Se lanza cuando se quiere trabajar con un club inexistente"""

    pass


class UsuarioNoEncontradoError(ErrorDeDominio):
    """Se lanza cuando se intenta usar un usuario inexistente"""

    pass


class CredencialesInvalidasError(ErrorDeDominio):
    """Se lanza cuando se intenta acceder con contraseña incorrecta"""

    pass


class VinculoActivoExistenteError(ErrorDeDominio):
    """Se lanza cuando se intenta registrar un jugador en un club nuevo cuando todavia tiene un club."""

    pass
