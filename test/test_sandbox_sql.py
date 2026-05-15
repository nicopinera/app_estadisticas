import sqlite3, pytest
import config.rutas as r
from infraestructura.persistencia.database_manager import SQLIteManager

@pytest.fixture
def db_conexion():
    manager = SQLIteManager(
        db_path=":memory:", 
        schema_path=r.SCHEMA_SQL,
        views_path=r.VISTA_SQL,
        seed_path=r.SEED_SQL
    )
    
    conexion = manager.connect()
    manager.inicializar_schema()
    manager.cargar_seed()
    
    return conexion

def test_conexion(db_conexion):
    assert isinstance(db_conexion,sqlite3.Connection)

def test_select(db_conexion):
    db_conexion.row_factory = sqlite3.Row
    cursor = db_conexion.cursor()
    cursor.execute("SELECT * FROM v_partidos_resumen")
    partidos = cursor.fetchall()
    for p in partidos:
        print(f"🏀 {p['fecha']}: {p['clubLocal']} vs {p['clubVisitante']} (Torneo: {p['competencia']})")
    assert partidos != None

def test_insert(db_conexion):
    db_conexion.row_factory = sqlite3.Row
    cursor = db_conexion.cursor()
    
    cursor.execute("""
        INSERT INTO jugador (nombre, apellido, dni, anioNacimiento) 
        VALUES ('Facundo', 'Campazzo', 36123456, 1991)
    """)
    db_conexion.commit() # Guardamos los cambios
    
    # Comprobamos que se guardó
    cursor.execute("SELECT * FROM jugador WHERE apellido = 'Campazzo'")
    facu = cursor.fetchone()
    assert facu['nombre'] == 'Facundo'
    assert facu['apellido'] == 'Campazzo'
    assert facu['dni'] == 36123456
    assert facu['anioNacimiento'] == 1991


# def _consultas_y_locuras(db_conexion):
#    print("=== INICIANDO LABORATORIO SQL ===")

    # Para poder acceder a las columnas por nombre (ej: fila['nombre'])
#    db_conexion.row_factory = sqlite3.Row
#    cursor = db_conexion.cursor()

    # =======================================================
    # 2. TEST DE CONSULTAS (Probar las vistas y SELECTs)
    # =======================================================
#    print("=== PROBANDO CONSULTAS (SELECT) ===")
#    print("Buscando los partidos en la vista 'v_partidos_resumen'...")
    
#    cursor.execute("SELECT * FROM v_partidos_resumen")
#    partidos = cursor.fetchall()
    
#    for p in partidos:
#        print(f"🏀 {p['fecha']}: {p['clubLocal']} vs {p['clubVisitante']} (Torneo: {p['competencia']})")
#    print("-" * 50)

    # =======================================================
    # 3. TEST DE INSERCIÓN EXITOSA (INSERT)
    # =======================================================
#    print("\n=== PROBANDO INSERCIÓN (INSERT) ===")
#    print("Agregando un nuevo jugador a la base de datos...")
    
#    cursor.execute("""
#        INSERT INTO jugador (nombre, apellido, dni, anioNacimiento) 
#        VALUES ('Facundo', 'Campazzo', 36123456, 1991)
    """)
    db_conexion.commit() # Guardamos los cambios
    
    # Comprobamos que se guardó
    cursor.execute("SELECT * FROM jugador WHERE apellido = 'Campazzo'")
    facu = cursor.fetchone()
    assert facu['nombre'] == 'Facundo'
    assert facu['apellido'] == 'Campazzo'
    assert facu['dni'] == 36123456
    assert facu['anioNacimiento'] == 1991
    # print(f"✅ Jugador insertado con éxito: {facu['nombre']} {facu['apellido']} - DNI: {facu['dni']}")
    # print("-" * 50)

    # =======================================================
    # 4. TEST DE "COSAS LOCAS" (Forzar errores de SQL)
    # =======================================================
    print("\n=== PROBANDO COSAS LOCAS (Restricciones CHECK y FK) ===")
    
    # Locura 1: Intentar meter un partido con un club que no existe (id 999)
    print("⚠️ Intentando crear un partido con un club fantasma (Violación de Foreign Key)...")
    try:
        cursor.execute("""
#            INSERT INTO partido (fecha, estadio, idCompetencia, idClubLocal, idClubVisitante) 
#            VALUES ('2026-10-10', 'Estadio Fantasma', 1, 999, 1)
#        """)
#    except sqlite3.IntegrityError as e:
#        print(f"🛑 ¡Bloqueado por SQL! Error capturado: {e}")

    # Locura 2: Jugador con rebotes negativos
#    print("\n⚠️ Intentando cargar estadísticas con rebotes negativos (Violación de CHECK)...")
#    try:
#        cursor.execute("""
#            INSERT INTO jugadorPartido (idJugador, idPartido, idClub, rebotesDef) 
#            VALUES (1, 1, 1, -50)
#        """)
#    except sqlite3.IntegrityError as e:
#        print(f"🛑 ¡Bloqueado por SQL! Error capturado: {e}")

#    print("\n=== FIN DEL LABORATORIO SQL ===")
#    manager.close_connection()