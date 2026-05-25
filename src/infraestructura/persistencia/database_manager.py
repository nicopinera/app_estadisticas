import sqlite3
from infraestructura.logger import get_logger

logger = get_logger(__name__)
class SQLiteManager:
    def __init__(self,db_path,schema_path,views_path,seed_path=None,limpieza_path=None):
        self.db_path = db_path
        self.schema_path = schema_path
        self.views_path = views_path
        self.seed_path = seed_path
        self.limpieza_path = limpieza_path
        self.conexion = None
    
    def connect(self):
        if self.conexion is None:
            self.conexion = sqlite3.connect(self.db_path)
            self.conexion.execute("PRAGMA foreign_keys = ON;") # Activo las claves foraneas
            self.conexion.row_factory = sqlite3.Row # Habilito acceso por nombre de columnas
        return self.conexion
    
    def inicializar_schema(self):
        try:
            # 1. Cargamos las tablas (schema.sql)
            with open(self.schema_path,'r',encoding='utf-8') as archivo_sql:
                schema = archivo_sql.read()
            self.conexion.executescript(schema)
            
            # 2. Cargamos las vistas (views.sql) - si es que hay
            with open(self.views_path,'r',encoding='utf-8') as archivo_vistas:
                vistas = archivo_vistas.read()
            self.conexion.executescript(vistas)
            
            logger.info('Esquema de db y vistas creado correctamente')
        except (sqlite3.Error,FileNotFoundError,OSError) as e:
            logger.error(f"Error al crear la vistas o la db: {e}")
    
    def cargar_seed(self):
        try:
            with open(self.seed_path,'r',encoding='utf-8') as archivo_sql:
                schema = archivo_sql.read()
            self.conexion.executescript(schema)
            logger.info('Seed de datos cargado correctamente')
        except (sqlite3.Error,TypeError) as e:
            logger.error(f'Error al cargar seed de datos: {e}')
    
    def get_connection(self):
        if self.conexion is not None:
            return self.conexion
        else:
            return None
    
    def close_connection(self):
        if self.conexion is not None:
            self.conexion.close()
            self.conexion = None
    
    def limpieza(self):
        try:
            with open(self.limpieza_path,'r',encoding='utf-8') as archivo_sql:
                schema = archivo_sql.read()
            self.conexion.executescript(schema)
            logger.info('Limpieza correcta')
        except sqlite3.Error as e:
            logger.error(f'Error al limpiar base de datos: {e}')