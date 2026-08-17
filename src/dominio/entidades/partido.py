from dataclasses import dataclass


@dataclass
class Partido:
    fecha: str
    estadio: str | None
    idCompetencia: int
    idClubLocal: int
    idClubVisitante: int
    idPartido: int | None = None

    def __post_init__(self):
        if not isinstance(self.fecha, str):
            raise TypeError(f"fecha debe ser str, recibido {type(self.fecha).__name__}")
        if self.estadio is not None and not isinstance(self.estadio, str):
            raise TypeError(f"estadio debe ser str, recibido {type(self.estadio).__name__}")
        if not isinstance(self.idCompetencia, int):
            raise TypeError(f"idCompetencia debe ser int, recibido {type(self.idCompetencia).__name__}")
        if not isinstance(self.idClubLocal, int):
            raise TypeError(f"idClubLocal debe ser int, recibido {type(self.idClubLocal).__name__}")
        if not isinstance(self.idClubVisitante, int):
            raise TypeError(f"idClubVisitante debe ser int, recibido {type(self.idClubVisitante).__name__}")
        if self.idPartido is not None and not isinstance(self.idPartido, int):
            raise TypeError(f"idPartido debe ser int o None, recibido {type(self.idPartido).__name__}")


@dataclass
class JugadorPartido:
    idJugador: int
    idPartido: int
    idClub: int
    minutosJugados: float = 0
    puntos: int = 0
    t2c: int = 0
    t2l: int = 0
    t3c: int = 0
    t3l: int = 0
    t1c: int = 0
    t1l: int = 0
    rebotesDef: int = 0
    rebotesOf: int = 0
    asistencias: int = 0
    recuperos: int = 0
    perdidas: int = 0
    taponesRecibidos: int = 0
    taponesRealizados: int = 0
    faltasRecibidas: int = 0
    faltasCometidas: int = 0

    def __post_init__(self):
        if not isinstance(self.idJugador, int):
            raise TypeError(f"idJugador debe ser int, recibido {type(self.idJugador).__name__}")
        if not isinstance(self.idPartido, int):
            raise TypeError(f"idPartido debe ser int, recibido {type(self.idPartido).__name__}")
        if not isinstance(self.idClub, int):
            raise TypeError(f"idClub debe ser int, recibido {type(self.idClub).__name__}")
