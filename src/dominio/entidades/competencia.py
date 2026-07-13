from dataclasses import dataclass


@dataclass
class Competencia:
    nombre: str
    anio: int
    tipo: str | None = None
    idCompetencia: int | None = None


@dataclass
class Categoria:
    nombre: str
    idCategoria: int | None = None


@dataclass
class Inscripcion:
    idClub: int
    idCategoria: int
    idCompetencia: int
    idInscripcion: int | None = None


@dataclass
class ListaBuenaFe:
    fechaPresentacion: str
    idInscripcion: int
    idListaBuenaFe: int | None = None


@dataclass
class JugadorListaBuenaFe:
    idJugador: int
    idListaBuenaFe: int
