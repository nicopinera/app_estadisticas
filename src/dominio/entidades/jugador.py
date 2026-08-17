from dataclasses import dataclass


@dataclass
class Jugador:
    nombre: str
    apellido: str
    dni: int
    anioNacimiento: int
    idJugador: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.nombre, str):
            raise TypeError(f"nombre debe ser str, recibido {type(self.nombre).__name__}")
        if not isinstance(self.apellido, str):
            raise TypeError(f"apellido debe ser str, recibido {type(self.apellido).__name__}")
        if not isinstance(self.dni, int):
            raise TypeError(f"dni debe ser int, recibido {type(self.dni).__name__}")
        if not isinstance(self.anioNacimiento, int):
            raise TypeError(f"anioNacimiento debe ser int, recibido {type(self.anioNacimiento).__name__}")
        if self.idJugador is not None and not isinstance(self.idJugador, int):
            raise TypeError(f"idJugador debe ser int o None, recibido {type(self.idJugador).__name__}")


@dataclass
class JugadorClub:
    fechaDesde: str
    fechaHasta: str | None
    idJugador: int | None = None
    idClub: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.fechaDesde, str):
            raise TypeError(f"fechaDesde debe ser str, recibido {type(self.fechaDesde).__name__}")
        if self.fechaHasta is not None and not isinstance(self.fechaHasta, str):
            raise TypeError(f"fechaHasta debe ser str o None, recibido {type(self.fechaHasta).__name__}")
        if self.idJugador is not None and not isinstance(self.idJugador, int):
            raise TypeError(f"idJugador debe ser int o None, recibido {type(self.idJugador).__name__}")
        if self.idClub is not None and not isinstance(self.idClub, int):
            raise TypeError(f"idClub debe ser int o None, recibido {type(self.idClub).__name__}")
