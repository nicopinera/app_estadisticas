from infraestructura.persistencia.database_manager import SQLiteManager
from infraestructura.logger import get_logger
import config.rutas as r

logger = get_logger(__name__)


def main():
    logger.info("Ejecutando orquestador principal")
    pruebaSQL = SQLiteManager(
        r.DB_FILE, r.SCHEMA_SQL, r.VISTA_SQL, r.SEED_SQL, r.CLEAR_SQL
    )
    conexion_test = pruebaSQL.connect()  # Genero conexion a DB
    pruebaSQL.inicializar_schema()  # Inicio db
    pruebaSQL.close_connection()  # Cierro conexion con DB
    del conexion_test
    logger.info("Fin de programa")


if __name__ == "__main__":
    main()
