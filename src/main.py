from infraestructura.persistencia.database_manager import SQLIteManager
import config.rutas as r

def main():
    pruebaSQL = SQLIteManager(r.DB_FILE,r.SCHEMA_SQL,r.VISTA_SQL,r.SEED_SQL,r.CLEAR_SQL)
    conexion_test = pruebaSQL.connect()
    pruebaSQL.inicializar_schema()
    # pruebaSQL.cargar_seed()
    # pruebaSQL.limpieza()

if __name__=="__main__":
    main()