from dataclasses import dataclass


@dataclass
class Club:
    idClub: int | None = None
    nombre: str


@dataclass
class UsuarioClub:
    idUsuario: int | None = None
    idClub: int | None = None
    rol: str
