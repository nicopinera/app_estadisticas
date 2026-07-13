from dataclasses import dataclass


@dataclass
class Usuario:
    idUsuario: int | None = None
    nombre: str
    email: str
    pw: str
