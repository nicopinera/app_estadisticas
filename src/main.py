import argparse

import config.rutas as r
from infraestructura.logger import get_logger
from infraestructura.persistencia.database_manager import SQLiteManager
from infraestructura.ui.cli.commands import jugador_add

logger = get_logger(__name__)


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="stats")
    subparser = parser.add_subparsers(dest="comando")

    # Rama "jugador"
    parser_jugador = subparser.add_parser("jugador", help="Operaciones sobre jugadores")
    jugador_subparsers = parser_jugador.add_subparsers(dest="subcomando")

    parser_jugador_add = jugador_subparsers.add_parser("add", help="Registra un jugador nuevo")
    parser_jugador_add.add_argument("--nombre", required=True, help="NOMBRE: nombre del jugador - OBLIGATORIO")
    parser_jugador_add.add_argument("--apellido", required=True, help="APELLIDO: Apellido del jugador - OBLIGATORIO")
    parser_jugador_add.add_argument("--dni", type=int, required=True, help="DNI: DNI del jugador - OBLIGATORIO")
    parser_jugador_add.add_argument("--anio", type=int, required=True, help="AÑO: Año de nacimiento del jugador")
    parser_jugador_add.set_defaults(func=jugador_add.ejecutar)

    return parser


def inicializar_db() -> None:
    db = SQLiteManager(r.DB_FILE, r.SCHEMA_SQL, r.VISTA_SQL)
    db.connect()
    db.inicializar_schema()
    db.close_connection()


def main() -> None:
    """Orquesta el flujo principal de la aplicación.

    Crea una instancia de :class:`SQLiteManager`, establece la conexión con la
    base de datos SQLite, inicializa el esquema y las vistas, carga los datos
    semilla y cierra la conexión al finalizar.

    Returns:
        None
    """
    logger.info("Ejecutando orquestador principal")
    inicializar_db()

    parser = construir_parser()
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
    logger.info("Fin de programa")


if __name__ == "__main__":
    main()
