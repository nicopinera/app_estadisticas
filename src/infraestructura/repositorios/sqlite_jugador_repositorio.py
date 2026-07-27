import sqlite3
from typing import Optional


from dominio.entidades.jugador import Jugador
from dominio.repositorios.jugador_repositorio import JugadorRepositorio #importacion de la clase 'JugadorRepositorio'
from Infraestructura.persistencia.sqlite_conexion import SqliteConexion



class SquliteJugadorRepositorio(JugadorRepositorio):
    def __init__(self, conexion: SqliteConexion) -> None:
        self.conexion = conexion    # Implementacion de la intefaz 'JugadorRepositorio' para Operaciones CRUD
                                    # en la tabla Jugador de la BD

    def _row_to_entity(self, row: sqlite3.Row) -> Jugador:
    return Jugador(
        nombre=row["nombre"],
        email=row["email"],
        pw=row["pw"],
        id=row["id_jugador"]
        anioNacimiento=row["anioNacimiento"]
        # Funcion que toma una fila de la tabla Jugador de la base de datos y la convierte en una instancia,
        # que es una entidad del dominio de la aplicacion, en este caso un objeto de la clase Jugador   
    )                   

    def buscar_por_id(self, id_jugador: int) -> Optional[Jugador]:

        conexion = self.conexion.obtener_conexion() # Funcion que nos permite conectarnos a la BD
        cursor = conexion.cursor() # con este cursor ejecutamos las consultas SQL

        query = "SELECT * FROM Jugador WHERE id_jugador = ?" # esto sirve para buscar un jugador por su ID
        cursor.execute(query, (id_jugador,)) # ejecutamos la consulta SQL con el ID del jugador que queremos buscar
        row = cursor.fetchone() # acá saca la primer coincidencia que encuentra en la BD

        if row is None: # si no encuentra nada en la BD, retorna None
            return None

        return self._row_to_entity(row) # si encuentra un jugador, lo convierte en una entidad y lo retorna

    def buscar_por_dni(self, dni_jugador: int) -> Optional[Jugador]:
        conexion = self.conexion.obtener_conexion()
        cursor = conexion.cursor()

        query = "SELECT * FROM Jugador WHERE dni_jugador = ?" #Buscar un jugador por su DNI
        cursor.execute(query, (dni_jugador,))
        row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_entity(row)

    def buscar_por_club(self, idClub: int) -> list[Jugador]: #Busqueda de Jugadores por Club
        conexion = self.conexion.obtener_conexion()
        cursor = conexion.cursor()

        query = "SELECT * FROM Jugador WHERE id_club = ?" #Buscar un jugador por su ID de Club
        cursor.execute(query, (idClub,))

        rows = cursor.fetchall() #Funcion que devuelve todas las filas de la consulta SQL como una lista de tuplas

        if rows is None:
            return None

        return [self._row_to_entity(row) for row in rows] #Si encuentra jugadores, los convierte en entidades y los retorna como una lista


    def guardar(self, jugador: Jugador) -> Jugador:
        
        #Guarda un jugador en la base de datos.
        conexion = self.conexion.obtener_conexion() #Funcion de persistecia de una entidad en la BD
        cursor = conexion.cursor()

        if jugador.id is None: # Caso 1 = cuando un jugador no tiene ID(None), realizamos un 'iNSERT' para agregarlo a la BD

            query = "INSERT INTO Jugador (nombre, apellido, dni, anioNacimiento) VALUES (?, ?, ?, ?)"
            cursor.execute(query, (jugador.nombre, jugador.apellido, jugador.dni, jugador.anioNacimiento))
            conexion.commit()

            jugador.idJugador = cursor.lastrowid #Esto nos sirve para obtener el ID del jugador que acabamos de insertar en la BD y lo asignamos a la propiedad idJugador del objeto jugador
        else:

            query = "UPDATE Jugador SET nombre = ?, apellido = ?, dni = ?, anioNacimiento = ? WHERE id_jugador = ?"
            cursor.execute(query, (jugador.nombre, jugador.apellido, jugador.dni, jugador.anioNacimiento, jugador.id))
            conexion.commit()

        return jugador