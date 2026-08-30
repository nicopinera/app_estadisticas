from dataclasses import dataclass


@dataclass
class PartidoDTO:  # sale de ListarPartidosPorClubUseCase
    idPartido: int
    fecha: str
    estadio: str | None
    idCompetencia: int
    idClubLocal: int
    idClubVisitante: int
