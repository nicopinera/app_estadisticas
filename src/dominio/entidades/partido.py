from dataclasses import dataclass


@dataclass
class Partido:
    fecha: str
    estadio: str | None
    idCompetencia: int
    idClubLocal: int
    idClubVisitante: int
    idPartido: int | None = None

    def __post_init__(self) -> None:
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

    def __post_init__(self) -> None:
        if not isinstance(self.idJugador, int):
            raise TypeError(f"idJugador debe ser int, recibido {type(self.idJugador).__name__}")
        if not isinstance(self.idPartido, int):
            raise TypeError(f"idPartido debe ser int, recibido {type(self.idPartido).__name__}")
        if not isinstance(self.idClub, int):
            raise TypeError(f"idClub debe ser int, recibido {type(self.idClub).__name__}")
        if self.minutosJugados < 0.0 or self.minutosJugados > 48.0:
            raise ValueError(
                f"Minutos Jugados no puede ser menos a 0 o mayor a 48.0 - Valor actual: {self.minutosJugados}"
            )
        if self.puntos < 0 or self.puntos != (self.t2c * 2 + self.t3c * 3 + self.t1c):
            raise ValueError(f"Puntos no puede ser 0 o distinto de T2C*2 + T3C*3 + T1C - Valor actual {self.puntos}")
        if self.t2c > self.t2l:
            raise ValueError(f"T2C ({self.t2c}) no puede ser mayor que T2L ({self.t2l})")
        if self.t3c > self.t3l:
            raise ValueError(f"T3C ({self.t3c}) no puede ser mayor que T3L ({self.t3l})")
        if self.t1c > self.t1l:
            raise ValueError(f"T1C ({self.t1c}) no puede ser mayor que T1L ({self.t1l})")
        if self.rebotesDef < 0:
            raise ValueError(f"Rebotes defensivos no puede ser < 0 - Valor actual: {self.rebotesDef}")
        if self.rebotesOf < 0:
            raise ValueError(f"Rebotes ofensivos no puede ser < 0 - Valor actual: {self.rebotesOf}")
        if self.asistencias < 0:
            raise ValueError(f"Asistencias no puede ser < 0 - Valor actual: {self.asistencias}")
        if self.recuperos < 0:
            raise ValueError(f"Recuperos no puede ser < 0 - Valor actual: {self.recuperos}")
        if self.perdidas < 0:
            raise ValueError(f"Perdidas no puede ser < 0 - Valor actual: {self.perdidas}")
        if self.taponesRecibidos < 0:
            raise ValueError(f"Tapones Recibidos no puede ser < 0 - Valor actual: {self.taponesRecibidos}")
        if self.taponesRealizados < 0:
            raise ValueError(f"Tapones Realizados no puede ser < 0 - Valor actual: {self.taponesRealizados}")
        if self.faltasRecibidas < 0:
            raise ValueError(f"Faltas Recibidas no puede ser < 0 - Valor actual: {self.faltasRecibidas}")
        if self.faltasCometidas < 0:
            raise ValueError(f"Faltas Cometidas no puede ser < 0 - Valor actual: {self.faltasCometidas}")
