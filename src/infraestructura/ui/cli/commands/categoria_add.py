import argparse

from aplicacion.casos_uso.crear_categoria import CrearCategoriaUseCase
from aplicacion.dtos.categoria_dto import CrearCategoriaDTO
from dominio.repositorios.competencia_repositorio import CompetenciaRepositorio
from infraestructura.persistencia.database_manager import abrir_conexion
from infraestructura.repositorios.sqlite_competencia_repositorio import SqliteCompetenciaRepositorio
from utils import abortar


def ejecutar(args: argparse.Namespace, repo: CompetenciaRepositorio | None = None) -> None:
    """Comando `categoria add`: crea una categoria nueva (ej. U21).

    Args:
        args (argparse.Namespace): Argumentos parseados (nombre).
        repo (CompetenciaRepositorio | None): Repositorio a usar. En produccion no se pasa (se arma contra
            SQLite real); en los tests se inyecta uno falso.
    """
    if repo is None:
        repo = SqliteCompetenciaRepositorio(conexion=abrir_conexion())

    categoria = CrearCategoriaUseCase(repo).ejecutar(CrearCategoriaDTO(nombre=args.nombre))
    if categoria is None:
        abortar("no se pudo guardar la categoria")
    print(f"Categoria creada: {categoria.nombre} (id={categoria.idCategoria})")
