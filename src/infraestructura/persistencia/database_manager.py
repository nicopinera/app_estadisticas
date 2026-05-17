import config.rutas as r
import sqlite3

class SQLIteManager:
    def __init__(self,db_path,schema_path,views_path,seed_path=None,limpieza_path=None):
        self.db_path = db_path
        self.schema_path = schema_path
        self.views_path = views_path
        self.seed_path = seed_path
        self.limpieza_path = limpieza_path
        self.conexion = None
    
    def connect(self):
        if self.conexion == None:
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
            
            print("Script de creacion de schema y vistas ejecutado")
        except sqlite3.Error as e:
            print(f"Error al crear la DB: {e}")
    
    def cargar_seed(self):
        try:
            with open(self.seed_path,'r',encoding='utf-8') as archivo_sql:
                schema = archivo_sql.read()
            self.conexion.executescript(schema)
            print("Script de seed ejecutado")
        except sqlite3.Error as e:
            print(f"Error al crear seed: {e}")
    
    def get_connection(self):
        if self.conexion != None:
            return self.conexion
        else:
            return None
    
    def close_connection(self):
        if self.conexion != None:
            self.conexion.close()
    
    def limpieza(self):
        try:
            with open(self.limpieza_path,'r',encoding='utf-8') as archivo_sql:
                schema = archivo_sql.read()
            self.conexion.executescript(schema)
            print("Script de limpieza ejecutado")
        except sqlite3.Error as e:
            print(f"Error al ejecutar la limpieza: {e}")