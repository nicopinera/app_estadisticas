import sqlite3
from typing import Optional

from dominio.entidades.club import Club, UsuarioClub
from dominio.repositorios.club_repositorio import ClubRepositorio
from infraestructura.persistencia.sqlite_conexion import SqliteConexion


class SqliteClubRepositorio(ClubRepositorio):
    def __init__(self, conexion: SqliteConexion) -> None:
        self.conexion = conexion

    def _row_to_entity(self, row: sqlite3.Row) -> Club:
        return Club(
            idClub=row["idClub"],
            nombre=row["nombre"],
        )

    def buscar_por_id_usuario(self, id_usuario: int) -> list[Club]:
        conexion = self.conexion.obtener_conexion()
        cursor = conexion.cursor()

        query = "SELECT c.* FROM Club c JOIN UsuarioClub uc ON c.idClub = uc.idClub WHERE uc.idUsuario = ?"
        cursor.execute(query, (id_usuario,))
        rows = cursor.fetchall()
        if row is None:
            return None
        return [self._row_to_entity(row) for row in row]

    def buscar_por_id(self, id_club: int) -> Club:
        conexion = self.conexion.obtener_conexion()
        cursor = conexion.cursor()

        query = "SELECT * FROM Club WHERE idClub = ?"
        cursor.execute(query, (id_club,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_entity(row)

    def buscar_por_nombre(self, nombre: str) -> list[Club]:
        conexion = self.conexion.obtener_conexion()
        cursor = conexion.cursor()

        query = "SELECT * FROM Club WHERE nombre LIKE ?"
        cursor.execute(query, (f"%{nombre}%",))
        rows = cursor.fetchall()
        if rows is None:
            return None
        return [self._row_to_entity(row) for row in rows]

    def guardar(self, nombre: str) -> Club:
        conexion = self.conexion.obtener_conexion()
        cursor = conexion.cursor()
        id_club = None

        if id_club is None:

            query = "INSERT INTO Club (nombre) VALUES (?)"
            cursor.execute(query, (nombre,))
            conexion.commit()

            id_club = cursor.lastrowid
        else:
            query = "UPDATE Club SET nombre = ? WHERE idClub = ?"
            cursor.execute(query, (nombre, id_club))
            conexion.commit()
            
        return Club(idClub=id_club, nombre=nombre)

    def link_user_to_club(self, idUsuario: int, idClub: int, rol: str) -> UsuarioClub:
        conexion = self.conexion.obtener_conexion()
        cursor = conexion.cursor()
        # Funcion para linkear un usuario a un club especifico
        query = "INSERT INTO UsuarioClub (idUsuario, idClub, rol) VALUES (?, ?, ?)"
        cursor.execute(query, (idUsuario, idClub, rol))
        conexion.commit()

        return UsuarioClub(idUsuario=idUsuario, idClub=idClub, rol=rol)

    

    