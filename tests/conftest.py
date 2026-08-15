import sqlite3

import pytest

import config.rutas as ruta
from infraestructura.persistencia.database_manager import SQLiteManager


@pytest.fixture
def db_conexion():
    conexion = sqlite3.connect(":memory:")
    cursor = conexion.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    with open(ruta.SCHEMA_SQL, "r") as schema:
        cursor.executescript(schema.read())

    with open(ruta.VISTA_SQL, "r") as schema:
        cursor.executescript(schema.read())

    with open(ruta.SEED_SQL, "r") as seed:
        cursor.executescript(seed.read())
    conexion.row_factory = sqlite3.Row

    yield conexion
    conexion.close()


@pytest.fixture
def db_conexion_sin_seed():
    conexion = sqlite3.connect(":memory:")
    cursor = conexion.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    with open(ruta.SCHEMA_SQL, "r") as schema:
        cursor.executescript(schema.read())

    with open(ruta.VISTA_SQL, "r") as schema:
        cursor.executescript(schema.read())

    conexion.row_factory = sqlite3.Row

    yield conexion
    conexion.close()


@pytest.fixture
def db_conexion_sandbox():
    manager = SQLiteManager(
        db_path=":memory:",
        schema_path=ruta.SCHEMA_SQL,
        views_path=ruta.VISTA_SQL,
        seed_path=ruta.SEED_SQL,
    )

    conexion = manager.connect()
    manager.inicializar_schema()
    manager.cargar_seed()

    return conexion
