import config.rutas as r
from infraestructura.logger import get_logger
from infraestructura.persistencia.database_manager import SQLiteManager

logger = get_logger(__name__)


def main():
    """Orquesta el flujo principal de la aplicación.

    Crea una instancia de :class:`SQLiteManager`, establece la conexión con la
    base de datos SQLite, inicializa el esquema y las vistas, carga los datos
    semilla y cierra la conexión al finalizar.

    Returns:
        None
    """
    logger.info("Ejecutando orquestador principal")
    pruebaSQL = SQLiteManager(r.DB_FILE, r.SCHEMA_SQL, r.VISTA_SQL, r.SEED_SQL, r.CLEAR_SQL)
    conexion_test = pruebaSQL.connect()  # Genero conexion a DB
    pruebaSQL.inicializar_schema()  # Inicio db
    pruebaSQL.cargar_seed()
    # pruebaSQL.limpieza()
    pruebaSQL.close_connection()  # Cierro conexion con DB
    del conexion_test
    logger.info("Fin de programa")


if __name__ == "__main__":
    main()
