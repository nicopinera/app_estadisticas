import argparse

import config.rutas as r
from aplicacion.casos_uso.registrar_jugador import RegistrarJugadorUseCase
from aplicacion.dtos.jugador_dto import CrearJugadorDTO
from dominio.exceptions import DNIDuplicadoError
from dominio.repositorios.jugador_repositorio import JugadorRepositorio
from infraestructura.persistencia.database_manager import SQLiteManager
from infraestructura.repositorios.sqlite_jugador_repositorio import SqliteJugadorRepositorio


def ejecutar(args: argparse.Namespace, repo: JugadorRepositorio | None = None) -> None:
    if repo is None:
        db = SQLiteManager(r.DB_FILE, r.SCHEMA_SQL, r.VISTA_SQL)
        conexion = db.connect()
        repo = SqliteJugadorRepositorio(conexion=conexion)

    dto = CrearJugadorDTO(nombre=args.nombre, apellido=args.apellido, dni=args.dni, anioNacimiento=args.anio)

    caso_uso = RegistrarJugadorUseCase(repo)
    try:
        jugador = caso_uso.ejecutar(dto)
        print(f"Jugador creado: {jugador.nombre} {jugador.apellido} (id={jugador.idJugador})")
    except DNIDuplicadoError as e:
        print(f"Error: {e}")
