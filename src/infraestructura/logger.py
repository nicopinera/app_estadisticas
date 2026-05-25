import logging
from logging.handlers import RotatingFileHandler
import os
import config.rutas as r


def crear_carpeta_logs():
    """Creacion de la carpeta para almacenar los logs"""
    os.makedirs(r.LOG_DIR, exist_ok=True)


def configuracion_log():
    crear_carpeta_logs()
    # Al no pasarle nombre configura el logger raiz, que es el padre de todos los loggers.
    # Esto hace que cualquier logger que se cree en la aplicación herede esta configuración.
    logger = logging.getLogger()

    # Esto para evitar que hayan handlers duplicados si se llama varias veces a get_logger()
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # A diferencia del FileHandler simple, este no llena el disco.
    # Cuando el archivo app.log llega a 10MB, se cierra.
    # backupCount=5; El sistema renombra el viejo a app.log.1, app.log.2... y así hasta 5. CUando llega al 6 borra el mas viejo
    app_handler = RotatingFileHandler(
        r.APP_LOG_FILE, maxBytes=10_000_000, backupCount=5, encoding="utf-8"
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(formatter)

    logger.addHandler(app_handler)

    return logger


def get_logger(name=None):
    """Obtener loger"""
    configuracion_log()
    return logging.getLogger(name)
