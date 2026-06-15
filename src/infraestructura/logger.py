import logging
import os
from logging.handlers import RotatingFileHandler

import config.rutas as r


def crear_carpeta_logs():
    """Crea el directorio de logs si no existe.

    Utiliza :data:`config.rutas.LOG_DIR` como ruta destino. La operación es
    idempotente: no lanza excepción si el directorio ya existe.

    Returns:
        None
    """
    os.makedirs(r.LOG_DIR, exist_ok=True)


def configuracion_log():
    """Configura el logger raíz de la aplicación.

    Instala un :class:`~logging.handlers.RotatingFileHandler` sobre el logger
    raíz con las siguientes características:

    - Nivel de registro: ``DEBUG`` para el logger, ``INFO`` para el handler.
    - Rotación automática al alcanzar 10 MB por archivo.
    - Conserva hasta 5 archivos de respaldo (``app.log.1`` … ``app.log.5``).
    - Formato: ``asctime - name - levelname - message``.

    Si el logger raíz ya tiene handlers configurados no agrega duplicados y
    retorna directamente.

    Returns:
        logging.Logger: instancia del logger raíz ya configurado.
    """
    crear_carpeta_logs()
    # Al no pasarle nombre configura el logger raiz,
    # que es el padre de todos los loggers.
    # Esto hace que cualquier logger que se cree en
    # la aplicación herede esta configuración.
    logger = logging.getLogger()

    # Esto para evitar que hayan handlers duplicados
    # si se llama varias veces a get_logger()
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # A diferencia del FileHandler simple, este no llena el disco.
    # Cuando el archivo app.log llega a 10MB, se cierra.
    # backupCount=5; El sistema renombra el viejo a app.log.1, app.log.2. y así hasta 5
    # Cuando llega al 6 borra el mas viejo
    app_handler = RotatingFileHandler(
        r.APP_LOG_FILE, maxBytes=10_000_000, backupCount=5, encoding="utf-8"
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(formatter)

    logger.addHandler(app_handler)

    return logger


def get_logger(name=None):
    """Devuelve un logger listo para usar en cualquier módulo.

    Llama internamente a :func:`configuracion_log` para garantizar que el
    logger raíz esté inicializado antes de retornar el logger solicitado.

    Args:
        name (str | None): Nombre del logger, normalmente ``__name__`` del
            módulo que lo invoca. Si es ``None`` se devuelve el logger raíz.

    Returns:
        logging.Logger: logger con nombre ``name`` que hereda la configuración
        del logger raíz.
    """
    configuracion_log()
    return logging.getLogger(name)
