from dataclasses import dataclass


@dataclass
class Usuario:
    nombre: str
    email: str
    pw: str
    idUsuario: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.nombre, str):
            raise TypeError(f"nombre debe ser str, recibido {type(self.nombre).__name__}")
        if not isinstance(self.email, str):
            raise TypeError(f"Email debe ser str, recibido {type(self.email).__name__}")
        if not isinstance(self.pw, str):
            raise TypeError(f"Password debe ser str, recibido {type(self.pw).__name__}")
        if self.idUsuario is not None and not isinstance(self.idUsuario, int):
            raise TypeError(f"idUsuario debe ser int o None, recibido {type(self.idUsuario).__name__}")
