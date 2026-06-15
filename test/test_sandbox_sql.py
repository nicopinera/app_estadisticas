import sqlite3
import pytest
import config.rutas as r
from infraestructura.persistencia.database_manager import SQLiteManager


@pytest.fixture
def db_conexion():
    manager = SQLiteManager(
        db_path=":memory:",
        schema_path=r.SCHEMA_SQL,
        views_path=r.VISTA_SQL,
        seed_path=r.SEED_SQL,
    )

    conexion = manager.connect()
    manager.inicializar_schema()
    manager.cargar_seed()

    return conexion


def test_conexion(db_conexion):
    assert isinstance(db_conexion, sqlite3.Connection)


def test_select(db_conexion):
    db_conexion.row_factory = sqlite3.Row
    cursor = db_conexion.cursor()
    cursor.execute("SELECT * FROM v_partidos_resumen")
    partidos = cursor.fetchall()
    assert partidos is not None


def test_insert(db_conexion):
    db_conexion.row_factory = sqlite3.Row
    cursor = db_conexion.cursor()

    cursor.execute(
        """
        INSERT INTO jugador (nombre, apellido, dni, anioNacimiento)
        VALUES ('Facundo', 'Campazzo', 36123456, 1991)
    """
    )
    db_conexion.commit()  # Guardamos los cambios

    # Comprobamos que se guardó
    cursor.execute("SELECT * FROM jugador WHERE apellido = 'Campazzo'")
    facu = cursor.fetchone()
    assert facu["nombre"] == "Facundo"
    assert facu["apellido"] == "Campazzo"
    assert facu["dni"] == 36123456
    assert facu["anioNacimiento"] == 1991
