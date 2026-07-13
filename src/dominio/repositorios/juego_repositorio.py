from abc import ABC, abstractmethod


class JuegoRepositorio(ABC):
    "Maneja partido y jugadorPartido"

    @abstractmethod
    def buscar_por_club(self, id_club: int) -> list:
        "Busca todos los partidos linkeados a un club"
        pass

    @abstractmethod
    def buscar_por_id(self):
        pass

    @abstractmethod
    def guardar_boxscore(self):
        pass
