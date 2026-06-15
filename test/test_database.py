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

    return conexion


def test_database_schema(db_conexion):
    tablas_esperadas = {
        "usuario",
        "club",
        "usuarioClub",
        "jugador",
        "jugadorClub",
        "competencia",
        "inscripcion",
        "listaBuenaFe",
        "jugadorListaBuenaFe",
        "partido",
        "jugadorPartido",
        "categoria",
    }

    cursor = db_conexion.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

    tablas_existentes = {row[0] for row in cursor.fetchall()}

    faltan = tablas_esperadas - tablas_existentes
    assert not faltan, f"Error: No se encontraron las tablas: {faltan}"


def test_database_schema_view(db_conexion):
    vistas_esperadas = {
        "v_jugador_totales_temporada",
        "v_listas_detalle",
        "v_boxscore_completo",
        "v_partidos_resumen",
    }

    cursor = db_conexion.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view';")

    vistas_existentes = {row[0] for row in cursor.fetchall()}

    faltan = vistas_esperadas - vistas_existentes
    assert not faltan, f"Error: No se encontraron las vistas: {faltan}"


def test_referential_integrity(db_conexion):
    # Intentar insertar un producto con una categoría que NO existe (id: 999)
    # Debe lanzar un sqlite3.IntegrityError
    db_cursor = db_conexion.cursor()
    with pytest.raises(sqlite3.IntegrityError):
        db_cursor.execute(
            "INSERT INTO listaBuenaFe (fechaPresentacion, idInscripcion) VALUES (?, ?)",
            ("2026-03-21", 1),
        )


def test_check_constraints(db_conexion):
    db_cursor = db_conexion.cursor()
    db_cursor.execute("PRAGMA foreign_keys = OFF;")
    # 1. Probar puntos negativos
    with pytest.raises(sqlite3.IntegrityError):
        db_cursor.execute(
            """INSERT INTO jugadorPartido
            (idJugador,idPartido,idClub,minutosJugados,T2C, T2L, T3C)
            VALUES (?, ?, ?,?,?,?,?)""",
            (1, 1, 1, 20, -20, -10, -30),
        )

    with pytest.raises(sqlite3.IntegrityError):
        db_cursor.execute(
            """INSERT INTO jugadorPartido
            (idJugador,idPartido,idClub,minutosJugados)
            VALUES (?, ?, ?, ?)""",
            (1, 1, 1, 49),
        )


def test_close_connection_cierra_la_conexion():
    manager = SQLiteManager(":memory:", ruta.SCHEMA_SQL, ruta.VISTA_SQL)
    conexion = manager.connect()

    manager.close_connection()

    with pytest.raises(sqlite3.ProgrammingError):
        conexion.execute("SELECT 1")


def test_limpieza_elimina_datos_de_seed():
    manager = SQLiteManager(
        ":memory:", ruta.SCHEMA_SQL, ruta.VISTA_SQL, ruta.SEED_SQL, ruta.CLEAR_SQL
    )
    conexion = manager.connect()
    manager.inicializar_schema()
    manager.cargar_seed()

    cursor = conexion.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM usuario WHERE nombre = ?", ("juan salvatierra",)
    )
    assert cursor.fetchone()[0] == 1

    manager.limpieza()

    cursor.execute(
        "SELECT COUNT(*) FROM usuario WHERE nombre = ?", ("juan salvatierra",)
    )
    assert cursor.fetchone()[0] == 0


def test_seed_execution_devuelve_datos_en_vistas():
    manager = SQLiteManager(":memory:", ruta.SCHEMA_SQL, ruta.VISTA_SQL, ruta.SEED_SQL)
    conexion = manager.connect()
    manager.inicializar_schema()
    manager.cargar_seed()

    cursor = conexion.cursor()
    cursor.execute("SELECT COUNT(*) FROM v_partidos_resumen")

    assert cursor.fetchone()[0] > 0


def test_division_by_zero_devuelve_cero_en_vistas():
    manager = SQLiteManager(":memory:", ruta.SCHEMA_SQL, ruta.VISTA_SQL, ruta.SEED_SQL)
    conexion = manager.connect()
    manager.inicializar_schema()
    manager.cargar_seed()

    cursor = conexion.cursor()
    cursor.execute(
        """INSERT INTO jugador (nombre, apellido, dni, anioNacimiento)
        VALUES (?, ?, ?, ?)""",
        ("Jugador", "Cero", 99999999, 2000),
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
        (
            id_jugador,
            id_partido,
            id_club,
            10,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ),
    )

    cursor.execute(
        """SELECT porcentaje_t2, porcentaje_t3, porcentaje_t1
        FROM v_jugador_totales_temporada
        WHERE nombre_jugador = ?""",
        ("Jugador Cero",),
    )
    porcentaje_t2, porcentaje_t3, porcentaje_t1 = cursor.fetchone()

    assert porcentaje_t2 == 0.0
    assert porcentaje_t3 == 0.0
    assert porcentaje_t1 == 0.0


def test_business_constraints(db_conexion):
    db_cursor = db_conexion.cursor()

    # Pre-requisitos: Clubes y Competencia
    db_cursor.execute("INSERT INTO club (nombre) VALUES ('Atenas')")
    db_cursor.execute("INSERT INTO club (nombre) VALUES ('Instituto')")
    db_cursor.execute(
        "INSERT INTO competencia (nombre, anio) VALUES ('Liga 2026', 2026)"
    )

    # 1. Probar que el local no sea igual al visitante
    with pytest.raises(sqlite3.IntegrityError):
        db_cursor.execute(
            "INSERT INTO partido (fecha, idCompetencia, idClubLocal, idClubVisitante) VALUES (?, ?, ?, ?)",
            ("2026-01-01", 1, 1, 1),  # ID local == ID visitante
        )

    # 2. Probar que tiros convertidos no superen a los lanzados (T2C <= T2L)
    # Pre-requisito: Jugador y Partido
    db_cursor.execute(
        "INSERT INTO jugador (nombre, apellido) VALUES ('Facundo', 'Campazzo')"
    )
    db_cursor.execute(
        "INSERT INTO partido (fecha, idCompetencia, idClubLocal, idClubVisitante) VALUES (?, ?, ?, ?)",
        ("2026-01-01", 1, 1, 2),
    )
    with pytest.raises(sqlite3.IntegrityError):
        db_cursor.execute(
            "INSERT INTO jugadorPartido (idJugador, idPartido, idClub, T2C, T2L) VALUES (?, ?, ?, ?, ?)",
            (1, 1, 1, 10, 5),  # 10 convertidos, 5 lanzados (IMPOSIBLE)
        )

    # 3. Año de competencia > 1900
    with pytest.raises(sqlite3.IntegrityError):
        db_cursor.execute(
            "INSERT INTO competencia (nombre, anio) VALUES ('Torneo Prehistórico', 1850)"
        )


def test_foreign_key_behavior(db_conexion):
    cursor = db_conexion.cursor()

    # Setup datos iniciales
    cursor.execute("INSERT INTO club (nombre) VALUES ('Atenas')")
    cursor.execute("INSERT INTO categoria (nombre) VALUES ('U21')")
    cursor.execute("INSERT INTO competencia (nombre, anio) VALUES ('Liga 2026', 2026)")
    cursor.execute(
        "INSERT INTO inscripcion (idClub, idCategoria, idCompetencia) VALUES (1, 1, 1)"
    )

    # 1. CASCADE: Al borrar competencia, se debe borrar la inscripción automáticamente
    cursor.execute("DELETE FROM competencia WHERE idCompetencia = 1")
    cursor.execute("SELECT COUNT(*) FROM inscripcion WHERE idCompetencia = 1")
    assert cursor.fetchone()[0] == 0

    # 2. RESTRICT: No se puede borrar un club si tiene registros en jugadorPartido
    # Re-insertamos datos necesarios
    cursor.execute("INSERT INTO club (nombre) VALUES ('Instituto')")  # idClub = 2
    cursor.execute(
        "INSERT INTO competencia (nombre, anio) VALUES ('Liga 2026 B', 2026)"
    )  # idCompetencia = 2
    cursor.execute(
        "INSERT INTO partido (fecha, idCompetencia, idClubLocal, idClubVisitante) VALUES (?, ?, ?, ?)",
        ("2026-01-01", 2, 1, 2),  # Local=1, Visitante=2
    )
    cursor.execute("INSERT INTO jugador (nombre, apellido) VALUES ('John', 'Doe')")
    cursor.execute(
        "INSERT INTO jugadorPartido (idJugador, idPartido, idClub, puntos) VALUES (1, 1, 1, 10)"
    )

    # Intentar borrar el club (debe fallar por el RESTRICT en jugadorPartido)
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute("DELETE FROM club WHERE idClub = 1")


def test_view_semantics_and_cardinality(db_conexion):
    # Setup: Inicializar con datos semilla
    manager = SQLiteManager(":memory:", ruta.SCHEMA_SQL, ruta.VISTA_SQL, ruta.SEED_SQL)
    conexion = manager.connect()
    manager.inicializar_schema()
    manager.cargar_seed()
    cursor = conexion.cursor()

    # 1. Validar v_partidos_resumen
    cursor.execute("SELECT * FROM v_partidos_resumen")
    columnas = [description[0] for description in cursor.description]
    datos = cursor.fetchall()
    assert set(columnas) == {
        "id_partido",
        "fecha_partido",
        "estadio",
        "competencia",
        "anio_competencia",
        "club_local",
        "club_visitante",
    }
    assert len(datos) == 2  # Hay 2 partidos en el seed

    # 2. Validar v_boxscore_completo
    cursor.execute("SELECT * FROM v_boxscore_completo")
    columnas = [description[0] for description in cursor.description]
    datos = cursor.fetchall()
    assert "nombre_jugador" in columnas
    assert "puntos" in columnas
    assert "rebotes_totales" in columnas
    assert len(datos) == 3  # Hay 3 registros de estadísticas en el seed

    # 3. Validar v_jugador_totales_temporada
    cursor.execute("SELECT * FROM v_jugador_totales_temporada")
    columnas = [description[0] for description in cursor.description]
    datos = cursor.fetchall()
    assert "total_puntos" in columnas
    assert "porcentaje_t3" in columnas
    assert "total_rebotes" in columnas
    assert len(datos) == 3  # 3 jugadores distintos con estadísticas

    # 4. Validar v_listas_detalle
    cursor.execute("SELECT * FROM v_listas_detalle")
    columnas = [description[0] for description in cursor.description]
    datos = cursor.fetchall()
    assert set(columnas) == {
        "id_inscripcion",
        "nombre_club",
        "nombre_categoria",
        "nombre_competencia",
        "nombre_jugador",
    }
    assert len(datos) == 10  # 10 jugadores en total en las listas de buena fe del seed
