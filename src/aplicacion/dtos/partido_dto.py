from dataclasses import dataclass


@dataclass
class PartidoResumenDTO:
    """Sale de ListarPartidosPorClubUseCase: un partido con los NOMBRES de la competencia y de los clubes"""

    idPartido: int
    fecha: str
    estadio: str | None
    competencia: str
    anioCompetencia: int
    clubLocal: str
    clubVisitante: str
