from abc import ABC, abstractmethod

from dominio.entidades.partido import JugadorPartido, Partido


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
    def guardar_partido(self, partido: Partido) -> Partido:
        pass

    @abstractmethod
    def guardar_boxscore(self, boxscore: JugadorPartido) -> JugadorPartido:
        pass
