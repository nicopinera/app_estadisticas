import os

RUTA_SRC = os.path.dirname(os.path.dirname(__file__))
SCHEMA_SQL = os.path.join(RUTA_SRC,'infraestructura','persistencia','sql','schema.sql')
VISTA_SQL = os.path.join(RUTA_SRC,'infraestructura','persistencia','sql','views.sql')
SEED_SQL = os.path.join(RUTA_SRC,'infraestructura','persistencia','sql','seed.sql')
CLEAR_SQL = os.path.join(RUTA_SRC,'infraestructura','persistencia','sql','limpieza.sql')
RUTA_RAIZ = os.path.dirname(RUTA_SRC)
DB_FILE = os.path.join(RUTA_RAIZ,'estadisticas.db')
LOG_DIR = os.path.join(RUTA_RAIZ,'logs')
APP_LOG_FILE = os.path.join(LOG_DIR, "app.log")