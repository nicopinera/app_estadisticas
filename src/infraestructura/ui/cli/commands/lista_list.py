import argparse

from aplicacion.casos_uso.listar_lista_buena_fe import ListarListaBuenaFeUseCase
from dominio.repositorios.competencia_repositorio import CompetenciaRepositorio
from dominio.repositorios.jugador_repositorio import JugadorRepositorio
from infraestructura.persistencia.database_manager import abrir_conexion
from infraestructura.repositorios.sqlite_competencia_repositorio import SqliteCompetenciaRepositorio
from infraestructura.repositorios.sqlite_jugador_repositorio import SqliteJugadorRepositorio
from infraestructura.ui.cli.formatters.table_formatter import formatear_tabla


def ejecutar(
    args: argparse.Namespace,
    repo_competencia: CompetenciaRepositorio | None = None,
    repo_jugador: JugadorRepositorio | None = None,
) -> None:
    """Comando `lista list`: lista en una tabla los jugadores habilitados en la lista de buena fe de una inscripcion.

    Args:
        args (argparse.Namespace): Argumentos parseados (id_inscripcion).
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

    jugadores = ListarListaBuenaFeUseCase(repo_competencia, repo_jugador).ejecutar(args.id_inscripcion)
    if not jugadores:
        print(f"La lista de buena fe de la inscripcion {args.id_inscripcion} no tiene jugadores.")
        return
    filas = [[j.id, j.nombre_completo, j.anioNacimiento] for j in jugadores]
    print(formatear_tabla(filas, ["ID", "Jugador", "Año de nacimiento"]))
