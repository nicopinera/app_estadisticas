from dataclasses import dataclass


@dataclass
class Usuario:
    nombre: str
    email: str
    pw: str
    idUsuario: int | None = None
