import argparse

from aplicacion.casos_uso.partidos_por_club import ListarPartidosPorClubUseCase
from dominio.repositorios.partido_repositorio import PartidoRepositorio
from infraestructura.persistencia.database_manager import abrir_conexion
from infraestructura.repositorios.sqlite_partido_repositorio import SqlitePartidoRepositorio
from infraestructura.ui.cli.formatters.table_formatter import formatear_tabla


def ejecutar(args: argparse.Namespace, repo: PartidoRepositorio | None = None) -> None:
    """Comando `partido list`: lista en una tabla los partidos de un club (como local o visitante).

    Args:
        args (argparse.Namespace): Argumentos parseados (id_club).
        repo (PartidoRepositorio | None): Repositorio a usar. En produccion no se pasa (se arma contra
            SQLite real); en los tests se inyecta uno falso.
    """
    if repo is None:
        repo = SqlitePartidoRepositorio(conexion=abrir_conexion())

    partidos = ListarPartidosPorClubUseCase(repo).ejecutar(args.id_club)
    if not partidos:
        print(f"El club {args.id_club} no tiene partidos.")
        return
    filas = [
        [p.idPartido, p.fecha, p.estadio or "-", f"{p.competencia} {p.anioCompetencia}", p.clubLocal, p.clubVisitante]
        for p in partidos
    ]
    print(formatear_tabla(filas, ["ID", "Fecha", "Estadio", "Competencia", "Club local", "Club visitante"]))
