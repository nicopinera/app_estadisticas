from abc import ABC, abstractmethod


class UsuarioRepositorio(ABC):
    @abstractmethod
    def encontrar_por_mail(self, email: str) -> set:
        "Busca un usuario por el mail"
        pass

    @abstractmethod
    def encontrar_por_id(self, id: int) -> set:
        "Busca usuario por id"
        pass

    @abstractmethod
    def guardar(self, nombre: str, email: str, pw: str) -> None:
        pass
