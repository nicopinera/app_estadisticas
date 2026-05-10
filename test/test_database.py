import sqlite3,pytest
import config.rutas as ruta

@pytest.fixture
def db_conexion():
    conexion = sqlite3.connect(":memory:")
    cursor = conexion.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    with open(ruta.SCHEMA_SQL,"r") as schema:
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
    