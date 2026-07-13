from abc import ABC, abstractmethod
from entidades.usuario import Usuario


class UsuarioRepositorio(ABC):
    @abstractmethod
    def encontrar_por_mail(self, email: str) -> Usuario:
        "Busca un usuario por el mail"
        pass

    @abstractmethod
    def encontrar_por_id(self, id: int) -> Usuario:
        "Busca usuario por id"
        pass

    @abstractmethod
    def guardar(self, nombre: str, email: str, pw: str) -> None:
        pass
