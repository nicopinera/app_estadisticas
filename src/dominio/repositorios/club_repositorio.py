from abc import ABC, abstractmethod

from dominio.entidades.club import Club, UsuarioClub


class ClubRepositorio(ABC):
    "Maneja Club y UsuarioClub"

    @abstractmethod
    def buscar_por_id_usuario(self, id_usuario: int) -> list[Club]:
        "Busca un club por id de usuario"
        pass

    @abstractmethod
    def buscar_por_id(self, id_club: int) -> Club:
        "Busca un club por id"
        pass

    @abstractmethod
    def buscar_por_nombre(self, nombre: str) -> list[Club]:
        "Busca un club por nombre"
        pass

    @abstractmethod
    def guardar(self, nombre: str) -> Club:
        "Guarda un Club, si es None, hay un error"
        pass

    @abstractmethod
    def link_user_to_club(self, idUsuario: int, idClub: int, rol: str) -> UsuarioClub:
        "Linkea un usuario a un club especifico"
        pass
