from abc import ABC, abstractmethod
from entidades.jugador import Jugador, JugadorClub
from entidades.club import Club


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
    def buscar_por_club(self, idClub: int) -> list[JugadorClub]:
        "Busca todos los jugadores de un club"
        pass

    @abstractmethod
    def guardar(
        self, nombre: str, apellido: str, dni: int, anioNacimiento: int
    ) -> None:
        pass

    @abstractmethod
    def link_to_club(self, id_jugador: int, id_club: int) -> None:
        "Vincula un jugador con un club, verificando link con otro club"
        pass

    @abstractmethod
    def club_activo(self, id_jugador: int, id_club: int) -> Club | None:
        "Devuelve el club activo de un jugador"
        pass
