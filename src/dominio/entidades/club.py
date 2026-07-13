from dataclasses import dataclass


@dataclass
class Club:
    nombre: str
    idClub: int | None = None


@dataclass
class UsuarioClub:
    rol: str
    idUsuario: int | None = None
    idClub: int | None = None
