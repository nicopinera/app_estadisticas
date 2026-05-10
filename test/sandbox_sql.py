import sys
import os
# --- INICIO DEL ARREGLO DE RUTA ---
# Esto le dice a Python que busque módulos en la carpeta 'src' 
# subiendo un nivel desde la carpeta actual 'test'
ruta_proyecto = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(ruta_proyecto)
# --- FIN DEL ARREGLO DE RUTA --
import sqlite3
import config.rutas as r
from infraestructura.persistencia.database_manager import SQLIteManager

def probar_consultas_y_locuras():
    print("=== INICIANDO LABORATORIO SQL ===")
    
    # 1. TEST DE CONEXIÓN
    # Usamos una base de datos en memoria para no romper la real
    manager = SQLIteManager(
        db_path=":memory:", 
        schema_path=r.SCHEMA_SQL,
        views_path=r.VISTA_SQL,
        seed_path=r.SEED_SQL
    )
    
    conexion = manager.connect()
    manager.inicializar_schema()
    manager.cargar_seed()
    print("✅ Conexión, tablas y datos semilla cargados.\n")

    # Para poder acceder a las columnas por nombre (ej: fila['nombre'])
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()

    # =======================================================
    # 2. TEST DE CONSULTAS (Probar las vistas y SELECTs)
    # =======================================================
    print("=== PROBANDO CONSULTAS (SELECT) ===")
    print("Buscando los partidos en la vista 'v_partidos_resumen'...")
    
    cursor.execute("SELECT * FROM v_partidos_resumen")
    partidos = cursor.fetchall()
    
    for p in partidos:
        print(f"🏀 {p['fecha']}: {p['clubLocal']} vs {p['clubVisitante']} (Torneo: {p['competencia']})")
    print("-" * 50)

    # =======================================================
    # 3. TEST DE INSERCIÓN EXITOSA (INSERT)
    # =======================================================
    print("\n=== PROBANDO INSERCIÓN (INSERT) ===")
    print("Agregando un nuevo jugador a la base de datos...")
    
    cursor.execute("""
        INSERT INTO jugador (nombre, apellido, dni, anioNacimiento) 
        VALUES ('Facundo', 'Campazzo', 36123456, 1991)
    """)
    conexion.commit() # Guardamos los cambios
    
    # Comprobamos que se guardó
    cursor.execute("SELECT * FROM jugador WHERE apellido = 'Campazzo'")
    facu = cursor.fetchone()
    print(f"✅ Jugador insertado con éxito: {facu['nombre']} {facu['apellido']} - DNI: {facu['dni']}")
    print("-" * 50)

    # =======================================================
    # 4. TEST DE "COSAS LOCAS" (Forzar errores de SQL)
    # =======================================================
    print("\n=== PROBANDO COSAS LOCAS (Restricciones CHECK y FK) ===")
    
    # Locura 1: Intentar meter un partido con un club que no existe (id 999)
    print("⚠️ Intentando crear un partido con un club fantasma (Violación de Foreign Key)...")
    try:
        cursor.execute("""
            INSERT INTO partido (fecha, estadio, idCompetencia, idClubLocal, idClubVisitante) 
            VALUES ('2026-10-10', 'Estadio Fantasma', 1, 999, 1)
        """)
    except sqlite3.IntegrityError as e:
        print(f"🛑 ¡Bloqueado por SQL! Error capturado: {e}")

    # Locura 2: Jugador con rebotes negativos
    print("\n⚠️ Intentando cargar estadísticas con rebotes negativos (Violación de CHECK)...")
    try:
        cursor.execute("""
            INSERT INTO jugadorPartido (idJugador, idPartido, idClub, rebotesDef) 
            VALUES (1, 1, 1, -50)
        """)
    except sqlite3.IntegrityError as e:
        print(f"🛑 ¡Bloqueado por SQL! Error capturado: {e}")

    print("\n=== FIN DEL LABORATORIO SQL ===")
    manager.close_connection()

if __name__ == "__main__":
    probar_consultas_y_locuras()