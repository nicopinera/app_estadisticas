import argparse

from aplicacion.casos_uso.listar_competencias import ListarCompetenciasUseCase
from dominio.repositorios.competencia_repositorio import CompetenciaRepositorio
from infraestructura.persistencia.database_manager import abrir_conexion
from infraestructura.repositorios.sqlite_competencia_repositorio import SqliteCompetenciaRepositorio
from infraestructura.ui.cli.formatters.table_formatter import formatear_tabla


def ejecutar(args: argparse.Namespace, repo: CompetenciaRepositorio | None = None) -> None:
    """Comando `competencia list`: lista en una tabla todas las competencias.

    Args:
        args (argparse.Namespace): Argumentos parseados (este comando no recibe ninguno).
        repo (CompetenciaRepositorio | None): Repositorio a usar. En produccion no se pasa (se arma contra
            SQLite real); en los tests se inyecta uno falso.
    """
    if repo is None:
        repo = SqliteCompetenciaRepositorio(conexion=abrir_conexion())

    competencias = ListarCompetenciasUseCase(repo).ejecutar()
    if not competencias:
        print("No hay competencias cargadas.")
        return
    filas = [[c.idCompetencia, c.nombre, c.anio, c.tipo or "-"] for c in competencias]
    print(formatear_tabla(filas, ["ID", "Competencia", "Año", "Tipo"]))
