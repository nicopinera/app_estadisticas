import argparse

from aplicacion.casos_uso.vincular_jugador_club import VincularJugadorAClubUseCase
from aplicacion.dtos.club_dto import VincularJugadorClubDTO
from dominio.repositorios.club_repositorio import ClubRepositorio
from dominio.repositorios.jugador_repositorio import JugadorRepositorio
from infraestructura.persistencia.database_manager import abrir_conexion
from infraestructura.repositorios.sqlite_club_repositorio import SqliteClubRepositorio
from infraestructura.repositorios.sqlite_jugador_repositorio import SqliteJugadorRepositorio
from utils import abortar


def ejecutar(
    args: argparse.Namespace,
    repo_jugador: JugadorRepositorio | None = None,
    repo_club: ClubRepositorio | None = None,
) -> None:
    """Comando `jugador link`: vincula un jugador a un club.

    Args:
        args (argparse.Namespace): Argumentos parseados (id_jugador, id_club, fecha_desde).
        repo_jugador (JugadorRepositorio | None): Repositorio de jugadores (se arma contra SQLite real si no se pasa).
        repo_club (ClubRepositorio | None): Repositorio de clubes (se arma contra SQLite real si no se pasa).
    """
    if repo_jugador is None or repo_club is None:
        conexion = abrir_conexion()
        repo_jugador = repo_jugador if repo_jugador is not None else SqliteJugadorRepositorio(conexion=conexion)
        repo_club = repo_club if repo_club is not None else SqliteClubRepositorio(conexion=conexion)

    dto = VincularJugadorClubDTO(idJugador=args.id_jugador, idClub=args.id_club, fechaDesde=args.fecha_desde)

    vinculo = VincularJugadorAClubUseCase(repo_jugador, repo_club).ejecutar(dto)
    if vinculo is None:
        abortar("no se pudo vincular el jugador al club")
    print(f"Jugador {vinculo.idJugador} vinculado al club {vinculo.idClub} desde {vinculo.fechaDesde}")
