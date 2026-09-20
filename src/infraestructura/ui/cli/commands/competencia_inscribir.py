import argparse

from aplicacion.casos_uso.inscribir_club_competencia import InscribirClubEnCompetenciaUseCase
from aplicacion.dtos.competencia_dto import InscribirClubDTO
from dominio.repositorios.club_repositorio import ClubRepositorio
from dominio.repositorios.competencia_repositorio import CompetenciaRepositorio
from infraestructura.persistencia.database_manager import abrir_conexion
from infraestructura.repositorios.sqlite_club_repositorio import SqliteClubRepositorio
from infraestructura.repositorios.sqlite_competencia_repositorio import SqliteCompetenciaRepositorio
from utils import abortar


def ejecutar(
    args: argparse.Namespace,
    repo_competencia: CompetenciaRepositorio | None = None,
    repo_club: ClubRepositorio | None = None,
) -> None:
    """Comando `competencia inscribir`: inscribe un club en una competencia y crea su lista de buena fe.

    Args:
        args (argparse.Namespace): Argumentos parseados (id_club, id_categoria, id_competencia, fecha_presentacion).
        repo_competencia (CompetenciaRepositorio | None): Repositorio de competencias (se arma contra SQLite real
            si no se pasa).
        repo_club (ClubRepositorio | None): Repositorio de clubes (se arma contra SQLite real si no se pasa).
    """
    if repo_competencia is None or repo_club is None:
        conexion = abrir_conexion()
        repo_competencia = (
            repo_competencia if repo_competencia is not None else SqliteCompetenciaRepositorio(conexion=conexion)
        )
        repo_club = repo_club if repo_club is not None else SqliteClubRepositorio(conexion=conexion)

    dto = InscribirClubDTO(
        idClub=args.id_club,
        idCategoria=args.id_categoria,
        idCompetencia=args.id_competencia,
        fechaPresentacion=args.fecha_presentacion,
    )

    inscripcion = InscribirClubEnCompetenciaUseCase(repo_competencia, repo_club).ejecutar(dto)
    if inscripcion is None:
        abortar("no se pudo guardar la inscripcion")
    print(
        f"Club {inscripcion.idClub} inscripto en la competencia {inscripcion.idCompetencia} "
        f"(categoria {inscripcion.idCategoria}). "
        f"Inscripcion id={inscripcion.idInscripcion}, lista de buena fe id={inscripcion.idListaBuenaFe}"
    )
