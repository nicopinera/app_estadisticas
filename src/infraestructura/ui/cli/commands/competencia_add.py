import argparse

from aplicacion.casos_uso.crear_competencia import CrearCompetenciaUseCase
from aplicacion.dtos.competencia_dto import CrearCompetenciaDTO
from dominio.repositorios.competencia_repositorio import CompetenciaRepositorio
from infraestructura.persistencia.database_manager import abrir_conexion
from infraestructura.repositorios.sqlite_competencia_repositorio import SqliteCompetenciaRepositorio
from utils import abortar


def ejecutar(args: argparse.Namespace, repo: CompetenciaRepositorio | None = None) -> None:
    """Comando `competencia add`: crea una competencia nueva.

    Args:
        args (argparse.Namespace): Argumentos parseados (nombre, anio, tipo).
        repo (CompetenciaRepositorio | None): Repositorio a usar. En produccion no se pasa (se arma contra
            SQLite real); en los tests se inyecta uno falso.
    """
    if repo is None:
        repo = SqliteCompetenciaRepositorio(conexion=abrir_conexion())

    dto = CrearCompetenciaDTO(nombre=args.nombre, anio=args.anio, tipo=args.tipo)

    # Un año invalido lanza DatoInvalidoError (ErrorDeDominio): no se atrapa aca, sube hasta main().
    competencia = CrearCompetenciaUseCase(repo).ejecutar(dto)
    if competencia is None:
        abortar("no se pudo guardar la competencia")
    print(f"Competencia creada: {competencia.nombre} {competencia.anio} (id={competencia.idCompetencia})")
