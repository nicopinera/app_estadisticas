from abc import ABC, abstractmethod

from entidades.partido import JugadorPartido, Partido


class JuegoRepositorio(ABC):
    "Maneja partido y jugadorPartido"

    @abstractmethod
    def buscar_por_club(self, id_club: int) -> list[Partido]:
        "Busca todos los partidos linkeados a un club"
        pass

    @abstractmethod
    def buscar_por_id(self, idPartido: int) -> Partido:
        "Busca la informacion de un partido"
        pass

    @abstractmethod
    def guardar_partido(
        self,
        fecha: str,
        estadio: str,
        idCompetencia: int,
        idClubLocal: int,
        idClubVisitante: int,
    ) -> Partido:
        pass

    @abstractmethod
    def guardar_boxscore(
        self,
        idJugador: int,
        idPartido: int,
        idClub: int,
        minutosJugados: int,
        puntos: int,
        t2c: int,
        t2l: int,
        t3c: int,
        t3l: int,
        t1c: int,
        t1l: int,
        rebotesDef: int,
        rebotesOf: int,
        asistencias: int,
        recuperos: int,
        perdidas: int,
        taponesRecibidos: int,
        taponesRealizados: int,
        faltasRecibidas: int,
        FaltasCometidas: int,
    ) -> JugadorPartido:
        pass
