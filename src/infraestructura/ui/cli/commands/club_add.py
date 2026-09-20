import argparse

from aplicacion.casos_uso.crear_club import CrearClubUseCase
from aplicacion.dtos.club_dto import CrearClubDTO
from dominio.repositorios.club_repositorio import ClubRepositorio
from infraestructura.persistencia.database_manager import abrir_conexion
from infraestructura.repositorios.sqlite_club_repositorio import SqliteClubRepositorio
from utils import abortar


def ejecutar(args: argparse.Namespace, repo: ClubRepositorio | None = None) -> None:
    """Comando `club add`: crea un club nuevo.

    Args:
        args (argparse.Namespace): Argumentos parseados (nombre).
        repo (ClubRepositorio | None): Repositorio a usar. En produccion no se pasa (se arma contra
            SQLite real); en los tests se inyecta uno falso.
    """
    if repo is None:
        repo = SqliteClubRepositorio(conexion=abrir_conexion())

    club = CrearClubUseCase(repo).ejecutar(CrearClubDTO(nombre=args.nombre))
    if club is None:
        abortar("no se pudo guardar el club")
    print(f"Club creado: {club.nombre} (id={club.idClub})")
