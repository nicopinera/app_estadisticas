import sqlite3
from typing import Optional


from dominio.entidades.usuario import Usuario
from dominio.repositorio.usuario_repositorio import UsuarioRepositorio
from infraestructura.persistencia.sqlite_conexion import SqliteConexion

 # importacion de la clase SqliteConexion para poder conectarse a la base de datos sqlite y la realizar operaciones CRUD 
 # en la tabla Usuarios, tambien se importa UsuarioRepositorio para la implementacion 
 
class SqliteUsuarioRepositorio(UsuarioRepositorio):
    def __init__(self, conexion: SqliteConexion) -> None:
        self.conexion = conexion
        # en este caso Implementa la interfaz UsuarioRepositorio y se encarga de realizar 
        # operaciones CRUD(Create, Read, Update, Delete) en la tabla Usuarios de la base de datos sqlite

    def _row_to_entity(self, row: sqlite3.Row) -> Usuario:
        return Usuario(
            nombre=row["nombre"],
            email=row["email"],
            pw=row["pw"],
            id=row["id_usuario"],
            # esta funcion toma una fila de la tabla Usuarios de la base de datos y la convierte en una instancia, 
            # que es una entidad del dominio de la aplicacion, en este caso un objeto de la clase Usuario
            )

    def buscar_por_id(self, id_usuario: int) -> optional[Usuario]:
        # Funcion se encarga de buscar a un usuario por su ID en el cual fue registrado en la BD
        # en el caso de que exista, retorna el usuario, sino retorna None si no se encuentra
        conexion = self.conexion.obtener_conexion() # con este conectamos a la BD
        cursor = conexion.cursor() # con este cursor ejecutamos las consultas SQL

        query = "SELECT * FROM Usuarios WHERE id_usuario = ?" # esto sirve para buscar un usuario por su ID
        cursor.execute(query, (id_usuario,)) # ejecutamos la consulta SQL con el ID del usuario que queremos buscar
        row = cursor.fetchone() # acá saca la primer coincidencia que encuentra en la BD

        if row is None: # si no encuentra nada en la BD, retorna None
            return None

        return self._row_to_entity(row) # si encuentra un usuario, lo convierte en una entidad y lo retorna

    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        conexion = self.conexion.obtener_conexion()
        cursor = conexion.cursor()

        query = "Select * from Usuarios where email = ?"      # Funcion para buscar un determinado Usuario por su direccion de mail
        cursor.execute(query, (email,))

        row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_entity(row)
        
    def guardar(self, usuario: Usuario) -> Usuario:     
                                                        
        Conexion = self.conexion.obtener_conexion() #Funcion de persistecia de una entidad en la BD 
        cursor = Conexion.cursor()

        if usuario.id is None:                          # Caso 1 = cuando un usuario no tiene ID(None), realizamos un 'iNSERT' para agregarlo a la BD

            query = "INSERT INTO Usuario (email, nombre, pw) VALUES (?, ?, ?)"
            cursor.execute(query, (usuario.email, usuario.nombre, usuario.pw))
            conexion.commit()

            usuario.idUsuario = cursor.lastrowid #Esto nos sirve para obtener el ID del usuario que acabamos de insertar en la BD y lo asignamos a la propiedad idUsuario del objeto usuario

        else:
            # Caso 2 = cuando un usuario ya tiene ID, realizamos un 'UPDATE' para actualizar sus datos en la BD 
            query = "UPDATE Usuario SET email = ?, nombre = ?, pw = ? WHERE id_usuario = ?"
            cursor.execute(query, (usuario.email, usuario.nombre, usuario.pw, usuario.id))
            conexion.commit()

        return usuario

    
    # Estos comentarios son de ayuda propia para poder entender que significa cada parte del codigo,
    # que hace cada funcion y como poder implementar las logica de negocio