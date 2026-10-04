import argparse

from aplicacion.casos_uso.listar_jugador_club import ListarJugadoresClubUseCase
from dominio.repositorios.jugador_repositorio import JugadorRepositorio
from infraestructura.persistencia.database_manager import abrir_conexion
from infraestructura.repositorios.sqlite_jugador_repositorio import SqliteJugadorRepositorio
from infraestructura.ui.cli.formatters.table_formatter import formatear_tabla


def ejecutar(args: argparse.Namespace, repo: JugadorRepositorio | None = None) -> None:
    """Comando `jugador list`: lista en una tabla los jugadores actuales de un club.

    Args:
        args (argparse.Namespace): Argumentos parseados (id_club).
        repo (JugadorRepositorio | None): Repositorio a usar. En produccion no se pasa (se arma contra
            SQLite real); en los tests se inyecta uno falso.
    """
    if repo is None:
        repo = SqliteJugadorRepositorio(conexion=abrir_conexion())

    jugadores = ListarJugadoresClubUseCase(repo).ejecutar(args.id_club)
    if not jugadores:
        print(f"El club {args.id_club} no tiene jugadores.")
        return
    print(
        formatear_tabla(
            [[j.id, j.nombre_completo, j.anioNacimiento] for j in jugadores],
            ["ID", "Jugador", "Año de nacimiento"],
        )
    )
