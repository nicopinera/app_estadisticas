"""Excepciones de dominio para la aplicacion de estadisticas."""


class ErrorDeDominio(Exception):
    """Clase base para todas las excepciones de dominio."""

    pass


class DNIDuplicadoError(ErrorDeDominio):
    """Se lanza cuando se intenta guardar un jugador con un DNI ya registrado."""

    pass
