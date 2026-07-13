from dataclasses import dataclass


@dataclass
class Jugador:
    nombre: str
    apellido: str
    dni: int
    anioNacimiento: int
    idJugador: int | None = None


@dataclass
class JugadorClub:
    fechaDesde: str
    fechaHasta: str | None
    idJugador: int | None = None
    idClub: int | None = None
