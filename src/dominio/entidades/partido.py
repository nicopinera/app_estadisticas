from dataclasses import dataclass


@dataclass
class Partido:
    fecha: str
    estadio: str | None
    idCompetencia: int
    idClubLocal: int
    idClubVisitante: int
    idPartido: int | None = None


@dataclass
class JugadorPartido:
    idJugador: int
    idPartido: int
    idClub: int
    minutosJugados: int = 0
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
