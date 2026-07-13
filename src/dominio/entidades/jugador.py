from dataclasses import dataclass


@dataclass
class Jugador:
    idjugador: int | None = None
    nombre: str
    apellido: str
    dni: int
    anioNacimiento: int


@dataclass
class JugadorClub:
    idJugador: int | None = None
    idClub: int | None = None
    fechaDesde: str
    fechaHasta: str | None
