import argparse

from aplicacion.casos_uso.quitar_jugador_lista import QuitarJugadorDeListaBuenaFeUseCase
from aplicacion.dtos.lista_buena_fe_dto import QuitarJugadorListaDTO
from dominio.repositorios.competencia_repositorio import CompetenciaRepositorio
from infraestructura.persistencia.database_manager import abrir_conexion
from infraestructura.repositorios.sqlite_competencia_repositorio import SqliteCompetenciaRepositorio
from utils import abortar


def ejecutar(args: argparse.Namespace, repo: CompetenciaRepositorio | None = None) -> None:
    """Comando `lista remove`: quita a un jugador de la lista de buena fe de una inscripcion.

    Args:
        args (argparse.Namespace): Argumentos parseados (id_inscripcion, id_jugador).
        repo (CompetenciaRepositorio | None): Repositorio a usar. En produccion no se pasa (se arma contra
            SQLite real); en los tests se inyecta uno falso.
    """
    if repo is None:
        repo = SqliteCompetenciaRepositorio(conexion=abrir_conexion())

    dto = QuitarJugadorListaDTO(idInscripcion=args.id_inscripcion, idJugador=args.id_jugador)

    quitado = QuitarJugadorDeListaBuenaFeUseCase(repo).ejecutar(dto)
    if quitado is None:
        abortar("no se pudo quitar al jugador de la lista de buena fe")
    print(
        f"Jugador {quitado.idJugador} quitado de la lista de buena fe {quitado.idListaBuenaFe} "
        f"(inscripcion {quitado.idInscripcion})"
    )
