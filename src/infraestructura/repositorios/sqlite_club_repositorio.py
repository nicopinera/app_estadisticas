import sqlite3

from dominio.entidades.club import Club, UsuarioClub
from dominio.repositorios.club_repositorio import ClubRepositorio


class SqliteClubRepositorio(ClubRepositorio):
    def __init__(self, conexion: sqlite3.Connection):
        self.conexion = conexion

    def _row_to_entity_Club(self, row: sqlite3.Row) -> Club:
        return Club(
            idClub=row["idClub"],
            nombre=row["nombre"],
        )

    def _row_to_entity_UsuarioClub(self, row: sqlite3.Row) -> UsuarioClub:
        return UsuarioClub(
            idClub=row["idClub"],
            idUsuario=row["idUsuario"],
            rol=row["rolEntrenador"],
        )

    def buscar_por_id_usuario(self, id_usuario: int) -> list[Club] | None:
        cursor = self.conexion.cursor()

        query = """
        SELECT c.idClub,c.nombre FROM club c
        JOIN usuarioClub uc ON c.idClub = uc.idClub
        WHERE uc.idUsuario = ?;
        """
        cursor.execute(query, (id_usuario,))
        rows = cursor.fetchall()
        if not rows:
            return None

        lista_clubes = []
        for r in rows:
            aux = self._row_to_entity_Club(r)
            lista_clubes.append(aux)
        return lista_clubes

    def buscar_por_id(self, id_club: int) -> Club:
        cursor = self.conexion.cursor()

        query = "SELECT * FROM club WHERE idClub = ?;"
        cursor.execute(query, (id_club,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_entity_Club(row)

    def buscar_por_nombre(self, nombre: str) -> list[Club]:
        cursor = self.conexion.cursor()

        query = "SELECT * FROM club WHERE nombre LIKE ?;"
        cursor.execute(query, (f"%{nombre}%",))
        rows = cursor.fetchall()
        if not rows:
            return None
        resultados = []
        for r in rows:
            aux = self._row_to_entity_Club(r)
            resultados.append(aux)
        return resultados

    def guardar(self, club: Club) -> Club:
        cursor = self.conexion.cursor()

        try:
            query = "INSERT INTO club (nombre) VALUES (?);"
            cursor.execute(query, (club.nombre,))
            self.conexion.commit()
            id_club = cursor.lastrowid
            return Club(idClub=id_club, nombre=club.nombre)
        except sqlite3.Error:
            return None

    def link_user_to_club(self, us_club: UsuarioClub) -> UsuarioClub:
        cursor = self.conexion.cursor()
        # Funcion para linkear un usuario a un club especifico
        try:
            query = """
            INSERT INTO usuarioClub (idUsuario, idClub, rolEntrenador) VALUES (?, ?, ?);
            """
            cursor.execute(query, (us_club.idUsuario, us_club.idClub, us_club.rol))
            self.conexion.commit()
            return UsuarioClub(
                idUsuario=us_club.idUsuario, idClub=us_club.idClub, rol=us_club.rol
            )
        except sqlite3.Error:
            return None
