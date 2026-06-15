from abc import ABC, abstractmethod


class ClubRepositorio(ABC):
    "Maneja Club y UsuarioClub"

    @abstractmethod
    def buscar_por_id_usuario(self, id_usuario: int) -> set:
        "Busca un club por id de usuario"
        pass

    @abstractmethod
    def buscar_por_id(self, id_club: int) -> set:
        "Busca un club por id"
        pass

    @abstractmethod
    def guardar(self, nombre: str) -> None:
        "Guarda un Club"
        pass
