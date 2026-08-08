import sqlite3

from dominio.entidades.usuario import Usuario
from dominio.repositorios.usuario_repositorio import UsuarioRepositorio

# importacion de la clase SqliteConexion para poder conectarse a la base de datos sqlite y la realizar operaciones CRUD  # noqa: E501
# en la tabla Usuarios, tambien se importa UsuarioRepositorio para la implementacion


class SqliteUsuarioRepositorio(UsuarioRepositorio):
    def __init__(self, conexion: sqlite3.Connection):
        self.conexion = conexion
        # en este caso Implementa la interfaz UsuarioRepositorio y se encarga de realizar  # noqa: E501
        # operaciones CRUD(Create, Read, Update, Delete) en la tabla Usuarios de la base de datos sqlite  # noqa: E501

    def _row_to_entity(self, row: sqlite3.Row) -> Usuario:
        return Usuario(
            nombre=row["nombre"],
            email=row["email"],
            pw=row["contrasenia"],
            idUsuario=row["idUsuario"],
            # esta funcion toma una fila de la tabla Usuarios de la base de datos y la convierte en una instancia,  # noqa: E501
            # que es una entidad del dominio de la aplicacion, en este caso un objeto de la clase Usuario  # noqa: E501
        )

    def encontrar_por_id(self, id: int) -> Usuario | None:
        # Funcion se encarga de buscar a un usuario por su ID en el cual fue registrado en la BD  # noqa: E501
        # en el caso de que exista, retorna el usuario, sino retorna None si no se encuentra  # noqa: E501
        # conexion = self.conexion.obtener_conexion()  # con este conectamos a la BD
        cursor = self.conexion.cursor()  # con este cursor ejecutamos las consultas SQL

        query = "SELECT * FROM usuario WHERE idUsuario = ?"  # esto sirve para buscar un usuario por su ID  # noqa: E501
        cursor.execute(
            query, (id,)
        )  # ejecutamos la consulta SQL con el ID del usuario que queremos buscar
        row = cursor.fetchone()
        # acá saca la primer coincidencia que encuentra en la BD

        if row is None:  # si no encuentra nada en la BD, retorna None
            return None

        # si encuentra un usuario, lo convierte en una entidad y lo retorna
        return self._row_to_entity(row)

    def encontrar_por_mail(self, email: str) -> Usuario | None:
        cursor = self.conexion.cursor()

        query = "SELECT * FROM usuario WHERE email = ?"  # Funcion para buscar un determinado Usuario por su direccion de mail  # noqa: E501
        cursor.execute(query, (email,))

        row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_entity(row)

    def guardar(self, us_aux: Usuario) -> Usuario:
        if not isinstance(us_aux.nombre, str):
            raise TypeError("nombre debe ser un string")
        if not isinstance(us_aux.email, str):
            raise TypeError("email debe ser un string")
        if not isinstance(us_aux.pw, str):
            raise TypeError("contraseña tiene que ser un string")

        cursor = self.conexion.cursor()
        query = "INSERT INTO usuario (email, nombre, contrasenia) VALUES (?, ?, ?)"
        cursor.execute(query, (us_aux.email, us_aux.nombre, us_aux.pw))
        self.conexion.commit()
        idUsuario = cursor.lastrowid
        return Usuario(
            nombre=us_aux.nombre, email=us_aux.email, pw=us_aux.pw, idUsuario=idUsuario
        )

    # Estos comentarios son de ayuda propia para poder entender que significa cada parte del codigo,  # noqa: E501
    # que hace cada funcion y como poder implementar las logica de negocio
