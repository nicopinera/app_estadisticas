from dataclasses import dataclass


@dataclass
class Competencia:
    nombre: str
    anio: int
    tipo: str | None = None
    idCompetencia: int | None = None

    def __post_init__(self):
        if not isinstance(self.nombre, str):
            raise TypeError(f"nombre debe ser str, recibido {type(self.nombre).__name__}")
        if not isinstance(self.anio, int):
            raise TypeError(f"anio debe ser int, recibido {type(self.anio).__name__}")
        if self.tipo is not None and not isinstance(self.tipo, str):
            raise TypeError(f"tipo debe ser str o None, recibido {type(self.tipo).__name__}")
        if self.idCompetencia is not None and not isinstance(self.idCompetencia, int):
            raise TypeError(f"idCompetencia debe ser int o None, recibido {type(self.idCompetencia).__name__}")


@dataclass
class Categoria:
    nombre: str
    idCategoria: int | None = None

    def __post_init__(self):
        if not isinstance(self.nombre, str):
            raise TypeError(f"nombre debe ser str, recibido {type(self.nombre).__name__}")
        if self.idCategoria is not None and not isinstance(self.idCategoria, int):
            raise TypeError(f"idCategoria debe ser int o None, recibido {type(self.idCategoria).__name__}")


@dataclass
class Inscripcion:
    idClub: int
    idCategoria: int
    idCompetencia: int
    idInscripcion: int | None = None

    def __post_init__(self):
        if not isinstance(self.idClub, int):
            raise TypeError(f"idClub debe ser int, recibido {type(self.idClub).__name__}")
        if not isinstance(self.idCategoria, int):
            raise TypeError(f"idCategoria debe ser int, recibido {type(self.idCategoria).__name__}")
        if not isinstance(self.idCompetencia, int):
            raise TypeError(f"idCompetencia debe ser int, recibido {type(self.idCompetencia).__name__}")
        if self.idInscripcion is not None and not isinstance(self.idInscripcion, int):
            raise TypeError(f"idInscripcion debe ser int o None, recibido {type(self.idInscripcion).__name__}")


@dataclass
class ListaBuenaFe:
    fechaPresentacion: str
    idInscripcion: int
    idListaBuenaFe: int | None = None

    def __post_init__(self):
        if not isinstance(self.fechaPresentacion, str):
            raise TypeError(f"fechaPresentacion debe ser str, recibido {type(self.fechaPresentacion).__name__}")
        if not isinstance(self.idInscripcion, int):
            raise TypeError(f"idInscripcion debe ser int, recibido {type(self.idInscripcion).__name__}")
        if self.idListaBuenaFe is not None and not isinstance(self.idListaBuenaFe, int):
            raise TypeError(f"idListaBuenaFe debe ser int o None, recibido {type(self.idListaBuenaFe).__name__}")


@dataclass
class JugadorListaBuenaFe:
    idJugador: int
    idListaBuenaFe: int

    def __post_init__(self):
        if not isinstance(self.idJugador, int):
            raise TypeError(f"idJugador debe ser int, recibido {type(self.idJugador).__name__}")
        if not isinstance(self.idListaBuenaFe, int):
            raise TypeError(f"idListaBuenaFe debe ser int, recibido {type(self.idListaBuenaFe).__name__}")
