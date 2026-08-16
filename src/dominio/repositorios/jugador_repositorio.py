from abc import ABC, abstractmethod

from dominio.entidades.club import Club
from dominio.entidades.jugador import Jugador, JugadorClub


class JugadorRepositorio(ABC):
    "Maneja Jugador y JugadorClub"

    @abstractmethod
    def buscar_por_id(self, id_jugador: int) -> Jugador | None:
        "Busca un jugador por id"
        pass

    @abstractmethod
    def buscar_por_dni(self, dni_jugador: int) -> Jugador | None:
        "Busca un jugador por DNI"
        pass

    @abstractmethod
    def buscar_por_club(self, idClub: int) -> list[Jugador] | None:
        "Busca todos los jugadores de un club"
        pass

    @abstractmethod
    def guardar(self, jugador: Jugador) -> Jugador | None:
        pass

    @abstractmethod
    def link_to_club(self, jc: JugadorClub) -> JugadorClub | None:
        "Vincula un jugador con un club, verificando link con otro club"
        pass

    @abstractmethod
    def club_activo(self, id_jugador: int) -> Club | None:
        "Devuelve el club activo de un jugador"
        pass
