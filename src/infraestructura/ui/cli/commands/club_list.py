import argparse

from aplicacion.casos_uso.listar_clubes_usr import ListarClubesUsuarioUseCase
from dominio.repositorios.club_repositorio import ClubRepositorio
from infraestructura.persistencia.database_manager import abrir_conexion
from infraestructura.repositorios.sqlite_club_repositorio import SqliteClubRepositorio
from infraestructura.ui.cli.formatters.table_formatter import formatear_tabla


def ejecutar(args: argparse.Namespace, repo: ClubRepositorio | None = None) -> None:
    """Comando `club list`: lista en una tabla los clubes de un usuario.

    Args:
        args (argparse.Namespace): Argumentos parseados (id_usuario).
        repo (ClubRepositorio | None): Repositorio a usar. En produccion no se pasa (se arma contra
            SQLite real); en los tests se inyecta uno falso.
    """
    if repo is None:
        repo = SqliteClubRepositorio(conexion=abrir_conexion())

    clubes = ListarClubesUsuarioUseCase(repo).ejecutar(args.id_usuario)
    if not clubes:
        print(f"El usuario {args.id_usuario} no pertenece a ningun club.")
        return
    print(formatear_tabla([[c.idClub, c.nombre] for c in clubes], ["ID", "Club"]))
