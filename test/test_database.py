import sqlite3,pytest
import config.rutas as ruta
from infraestructura.persistencia.database_manager import SQLIteManager

@pytest.fixture
def db_conexion():
    conexion = sqlite3.connect(":memory:")
    cursor = conexion.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    with open(ruta.SCHEMA_SQL,"r") as schema:
        cursor.executescript(schema.read())
    
    with open(ruta.VISTA_SQL,"r") as schema:
        cursor.executescript(schema.read())
    
    return conexion

def test_database_schema(db_conexion):
    tablas_esperadas={"usuario","club","usuarioClub","jugador","jugadorClub","competencia",
                      "inscripcion","listaBuenaFe","jugadorListaBuenaFe","partido","jugadorPartido","categoria"}
    
    cursor = db_conexion.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    
    tablas_existentes = {row[0] for row in cursor.fetchall()}
    
    faltan = tablas_esperadas-tablas_existentes
    assert not faltan, f"Error: No se encontraron las tablas: {faltan}"

def test_database_schema_view(db_conexion):
    vistas_esperadas={"v_jugador_totales_temporada","v_listas_detalle","v_boxscore_completo","v_partidos_resumen"}
    
    cursor = db_conexion.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view';")
    
    vistas_existentes = {row[0] for row in cursor.fetchall()}
    
    faltan = vistas_esperadas-vistas_existentes
    assert not faltan, f"Error: No se encontraron las vistas: {faltan}"

def test_referential_integrity(db_conexion):
    # Intentar insertar un producto con una categoría que NO existe (id: 999)
    # Debe lanzar un sqlite3.IntegrityError
    db_cursor = db_conexion.cursor()
    with pytest.raises(sqlite3.IntegrityError) as excinfo:
        db_cursor.execute(
            "INSERT INTO listaBuenaFe (fechaPresentacion, idInscripcion) VALUES (?, ?)", 
            ("2026-03-21", 1)
        )
    
    # Opcional: Verificar que el mensaje de error mencione la restricción
    assert "FOREIGN KEY constraint failed" in str(excinfo.value)

def test_check_constraints(db_conexion):
    db_cursor = db_conexion.cursor()
    db_cursor.execute("PRAGMA foreign_keys = OFF;")
    # 1. Probar puntos negativos
    with pytest.raises(sqlite3.IntegrityError) as excinfo:
        db_cursor.execute("INSERT INTO jugadorPartido (idJugador,idPartido,idClub,minutosJugados,T2C, T2L, T3C) VALUES (?, ?, ?,?,?,?,?)", (1,1,1,20,-20, -10, -30))
    assert "CHECK constraint failed" in str(excinfo.value)

    with pytest.raises(sqlite3.IntegrityError) as excinfo:
        db_cursor.execute("INSERT INTO jugadorPartido (idJugador,idPartido,idClub,minutosJugados) VALUES (?, ?, ?, ?)", (1,1,1,49))
    assert "CHECK constraint failed" in str(excinfo.value)

def test_close_connection_cierra_la_conexion():
    manager = SQLIteManager(":memory:", ruta.SCHEMA_SQL, ruta.VISTA_SQL)
    conexion = manager.connect()

    manager.close_connection()

    with pytest.raises(sqlite3.ProgrammingError):
        conexion.execute("SELECT 1")

def test_limpieza_elimina_datos_de_seed():
    manager = SQLIteManager(":memory:", ruta.SCHEMA_SQL, ruta.VISTA_SQL, ruta.SEED_SQL, ruta.CLEAR_SQL)
    conexion = manager.connect()
    manager.inicializar_schema()
    manager.cargar_seed()

    cursor = conexion.cursor()
    cursor.execute("SELECT COUNT(*) FROM usuario WHERE nombre = ?", ("juan salvatierra",))
    assert cursor.fetchone()[0] == 1

    manager.limpieza()

    cursor.execute("SELECT COUNT(*) FROM usuario WHERE nombre = ?", ("juan salvatierra",))
    assert cursor.fetchone()[0] == 0

def test_seed_execution_devuelve_datos_en_vistas():
    manager = SQLIteManager(":memory:", ruta.SCHEMA_SQL, ruta.VISTA_SQL, ruta.SEED_SQL)
    conexion = manager.connect()
    manager.inicializar_schema()
    manager.cargar_seed()

    cursor = conexion.cursor()
    cursor.execute("SELECT COUNT(*) FROM v_partidos_resumen")

    assert cursor.fetchone()[0] > 0

def test_division_by_zero_devuelve_cero_en_vistas():
    manager = SQLIteManager(":memory:", ruta.SCHEMA_SQL, ruta.VISTA_SQL, ruta.SEED_SQL)
    conexion = manager.connect()
    manager.inicializar_schema()
    manager.cargar_seed()

    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO jugador (nombre, apellido, dni, anioNacimiento) VALUES (?, ?, ?, ?)",
        ("Jugador", "Cero", 99999999, 2000)
    )
    id_jugador = cursor.lastrowid

    cursor.execute("SELECT idClub FROM club WHERE nombre = ?", ("Atenas",))
    id_club = cursor.fetchone()[0]
    cursor.execute("SELECT idPartido FROM partido WHERE fecha = ?", ("2026-05-21",))
    id_partido = cursor.fetchone()[0]

    cursor.execute(
        """
        INSERT INTO jugadorPartido (
            idJugador, idPartido, idClub, minutosJugados, puntos, T2C, T2L, T3C, T3L,
            T1C, T1L, rebotesDef, rebotesOf, asistencias, recuperos, perdidas,
            taponesRecibidos, taponesRealizados, faltasRecibidas, faltasCometidas
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (id_jugador, id_partido, id_club, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    )

    cursor.execute(
        "SELECT porcentaje_t2, porcentaje_t3, porcentaje_t1 FROM v_jugador_totales_temporada WHERE nombre_completo = ?",
        ("Jugador Cero",)
    )
    porcentaje_t2, porcentaje_t3, porcentaje_t1 = cursor.fetchone()

    assert porcentaje_t2 == 0.0
    assert porcentaje_t3 == 0.0
    assert porcentaje_t1 == 0.0