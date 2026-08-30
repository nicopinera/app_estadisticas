from dataclasses import dataclass


@dataclass
class CrearClubDTO:
    """Imgresaa CrearClubUseCase.ejecutar()"""

    nombre: str


@dataclass
class ClubDTO:
    """Sale de CrearClubuseCase / ListarClubesUsuarioUseCase"""

    idClub: int
    nombre: str


@dataclass
class VincularJugadorClubDTO:
    """entra a VincularJugadorAClubUseCase"""

    idJugador: int
    idClub: int
    fechaDesde: str
