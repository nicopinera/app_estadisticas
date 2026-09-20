import argparse

from aplicacion.casos_uso.listar_inscripciones_club import ListarInscripcionesClubUseCase
from dominio.repositorios.competencia_repositorio import CompetenciaRepositorio
from infraestructura.persistencia.database_manager import abrir_conexion
from infraestructura.repositorios.sqlite_competencia_repositorio import SqliteCompetenciaRepositorio
from infraestructura.ui.cli.formatters.table_formatter import formatear_tabla


def ejecutar(args: argparse.Namespace, repo: CompetenciaRepositorio | None = None) -> None:
    """Comando `inscripcion list`: lista en una tabla las inscripciones de un club.

    Args:
        args (argparse.Namespace): Argumentos parseados (id_club).
        repo (CompetenciaRepositorio | None): Repositorio a usar. En produccion no se pasa (se arma contra
            SQLite real); en los tests se inyecta uno falso.
    """
    if repo is None:
        repo = SqliteCompetenciaRepositorio(conexion=abrir_conexion())

    inscripciones = ListarInscripcionesClubUseCase(repo).ejecutar(args.id_club)
    if not inscripciones:
        print(f"El club {args.id_club} no tiene inscripciones.")
        return
    filas = [[i.idInscripcion, i.idCompetencia, i.idCategoria, i.idListaBuenaFe] for i in inscripciones]
    print(formatear_tabla(filas, ["ID inscripcion", "Competencia", "Categoria", "Lista de buena fe"]))
