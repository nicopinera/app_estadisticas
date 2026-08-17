from dataclasses import dataclass


@dataclass
class Club:
    nombre: str
    idClub: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.nombre, str):
            raise TypeError(f"nombre debe ser str, recibido {type(self.nombre).__name__}")
        if self.idClub is not None and not isinstance(self.idClub, int):
            raise TypeError(f"idClub debe ser int o None, recibido {type(self.idClub).__name__}")


@dataclass
class UsuarioClub:
    rol: str
    idUsuario: int | None = None
    idClub: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.rol, str):
            raise TypeError(f"rol debe ser str, recibido {type(self.rol).__name__}")
        if self.idUsuario is not None and not isinstance(self.idUsuario, int):
            raise TypeError(f"idUsuario debe ser int o None, recibido {type(self.idUsuario).__name__}")
        if self.idClub is not None and not isinstance(self.idClub, int):
            raise TypeError(f"idClub debe ser int o None, recibido {type(self.idClub).__name__}")
