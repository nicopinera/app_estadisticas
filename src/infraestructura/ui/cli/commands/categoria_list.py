import argparse

from aplicacion.casos_uso.listar_categorias import ListarCategoriasUseCase
from dominio.repositorios.competencia_repositorio import CompetenciaRepositorio
from infraestructura.persistencia.database_manager import abrir_conexion
from infraestructura.repositorios.sqlite_competencia_repositorio import SqliteCompetenciaRepositorio
from infraestructura.ui.cli.formatters.table_formatter import formatear_tabla


def ejecutar(args: argparse.Namespace, repo: CompetenciaRepositorio | None = None) -> None:
    """Comando `categoria list`: lista en una tabla todas las categorias.

    Args:
        args (argparse.Namespace): Argumentos parseados (este comando no recibe ninguno).
        repo (CompetenciaRepositorio | None): Repositorio a usar. En produccion no se pasa (se arma contra
            SQLite real); en los tests se inyecta uno falso.
    """
    if repo is None:
        repo = SqliteCompetenciaRepositorio(conexion=abrir_conexion())

    categorias = ListarCategoriasUseCase(repo).ejecutar()
    if not categorias:
        print("No hay categorias cargadas.")
        return
    print(formatear_tabla([[c.idCategoria, c.nombre] for c in categorias], ["ID", "Categoria"]))
