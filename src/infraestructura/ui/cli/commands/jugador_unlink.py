import argparse

from aplicacion.casos_uso.desvincular_jugador_club import DesvincularJugadorDeClubUseCase
from aplicacion.dtos.club_dto import DesvincularJugadorDTO
from dominio.repositorios.jugador_repositorio import JugadorRepositorio
from infraestructura.persistencia.database_manager import abrir_conexion
from infraestructura.repositorios.sqlite_jugador_repositorio import SqliteJugadorRepositorio
from utils import abortar


def ejecutar(args: argparse.Namespace, repo: JugadorRepositorio | None = None) -> None:
    """Comando `jugador unlink`: da de baja a un jugador de su club actual (cierra su vinculo vigente).

    Args:
        args (argparse.Namespace): Argumentos parseados (id_jugador, fecha_hasta).
        repo (JugadorRepositorio | None): Repositorio a usar. En produccion no se pasa (se arma contra
            SQLite real); en los tests se inyecta uno falso.
    """
    if repo is None:
        repo = SqliteJugadorRepositorio(conexion=abrir_conexion())

    dto = DesvincularJugadorDTO(idJugador=args.id_jugador, fechaHasta=args.fecha_hasta)

    vinculo = DesvincularJugadorDeClubUseCase(repo).ejecutar(dto)
    if vinculo is None:
        abortar("no se pudo desvincular al jugador del club")
    print(
        f"Jugador {vinculo.idJugador} desvinculado del club {vinculo.idClub} "
        f"(desde {vinculo.fechaDesde} hasta {vinculo.fechaHasta})"
    )
