import argparse

from aplicacion.casos_uso.agregar_jugador_lista import AgregarJugadorAListaBuenaFeUseCase
from aplicacion.dtos.lista_buena_fe_dto import AgregarJugadorListaDTO
from dominio.repositorios.competencia_repositorio import CompetenciaRepositorio
from dominio.repositorios.jugador_repositorio import JugadorRepositorio
from infraestructura.persistencia.database_manager import abrir_conexion
from infraestructura.repositorios.sqlite_competencia_repositorio import SqliteCompetenciaRepositorio
from infraestructura.repositorios.sqlite_jugador_repositorio import SqliteJugadorRepositorio
from utils import abortar


def ejecutar(
    args: argparse.Namespace,
    repo_competencia: CompetenciaRepositorio | None = None,
    repo_jugador: JugadorRepositorio | None = None,
) -> None:
    """Comando `lista add`: habilita a un jugador en la lista de buena fe de una inscripcion.

    Args:
        args (argparse.Namespace): Argumentos parseados (id_inscripcion, id_jugador).
        repo_competencia (CompetenciaRepositorio | None): Repositorio de competencias (se arma contra SQLite real
            si no se pasa).
        repo_jugador (JugadorRepositorio | None): Repositorio de jugadores (se arma contra SQLite real si no se pasa).
    """
    if repo_competencia is None or repo_jugador is None:
        conexion = abrir_conexion()
        repo_competencia = (
            repo_competencia if repo_competencia is not None else SqliteCompetenciaRepositorio(conexion=conexion)
        )
        repo_jugador = repo_jugador if repo_jugador is not None else SqliteJugadorRepositorio(conexion=conexion)

    dto = AgregarJugadorListaDTO(idInscripcion=args.id_inscripcion, idJugador=args.id_jugador)

    habilitado = AgregarJugadorAListaBuenaFeUseCase(repo_competencia, repo_jugador).ejecutar(dto)
    if habilitado is None:
        abortar("no se pudo agregar el jugador a la lista de buena fe")
    print(
        f"Jugador {habilitado.idJugador} habilitado en la lista de buena fe {habilitado.idListaBuenaFe} "
        f"(inscripcion {habilitado.idInscripcion})"
    )
