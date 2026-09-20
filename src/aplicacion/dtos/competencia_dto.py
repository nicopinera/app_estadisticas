from dataclasses import dataclass


@dataclass
class CrearCompetenciaDTO:
    "Entra a CrearCompetenciaUseCase"

    nombre: str
    anio: int
    tipo: str | None = None


@dataclass
class CompetenciaDTO:
    "Sale de CrearCompetenciaUseCase"

    idCompetencia: int
    nombre: str
    anio: int
    tipo: str | None


@dataclass
class InscribirClubDTO:
    "entra InscribirClubEnCompetenciaUseCase"

    idClub: int
    idCategoria: int
    idCompetencia: int
    fechaPresentacion: str


@dataclass
class InscripcionDTO:  # sale de InscribirClubEnCompetenciaUseCase
    idInscripcion: int
    idClub: int
    idCategoria: int
    idCompetencia: int
    idListaBuenaFe: int
