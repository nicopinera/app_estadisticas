import sqlite3

from dominio.entidades.club import Club
from dominio.entidades.jugador import Jugador, JugadorClub
from dominio.repositorios.jugador_repositorio import JugadorRepositorio


class SqliteJugadorRepositorio(JugadorRepositorio):
    def __init__(self, conexion: sqlite3.Connection):
        self.conexion = conexion

    def _row_to_entity(self, row: sqlite3.Row) -> Jugador:
        return Jugador(
            nombre=row["nombre"],
            apellido=row["apellido"],
            dni=row["dni"],
            anioNacimiento=row["anioNacimiento"],
            idJugador=row["idJugador"],
        )

    def buscar_por_id(self, id_jugador: int) -> Jugador | None:
        cursor = self.conexion.cursor()

        query = "SELECT * FROM jugador WHERE idJugador = ?"
        cursor.execute(query, (id_jugador,))
        row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_entity(row)

    def buscar_por_dni(self, dni_jugador: int) -> Jugador | None:
        cursor = self.conexion.cursor()

        query = "SELECT * FROM jugador WHERE dni = ?"
        cursor.execute(query, (dni_jugador,))
        row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_entity(row)

    def buscar_por_club(self, idClub: int) -> list[Jugador]:
        cursor = self.conexion.cursor()

        query = """
        SELECT j.idJugador,j.nombre,j.apellido,j.dni,j.anioNacimiento
        FROM jugadorClub jc
        JOIN jugador j ON j.idJugador = jc.idJugador
        WHERE jc.idClub = ?;
        """
        cursor.execute(query, (idClub,))

        rows = cursor.fetchall()
        if not rows:
            return None

        resultado = []
        for r in rows:
            j_aux = self._row_to_entity(r)
            resultado.append(j_aux)
        return resultado

    def guardar(self, jugador: Jugador) -> Jugador:
        cursor = self.conexion.cursor()
        try:
            query = "INSERT INTO jugador (nombre, apellido, dni, anioNacimiento) VALUES (?, ?, ?, ?);"
            cursor.execute(
                query,
                (jugador.nombre, jugador.apellido, jugador.dni, jugador.anioNacimiento),
            )
            self.conexion.commit()
            id_jugador = cursor.lastrowid

            return Jugador(
                nombre=jugador.nombre,
                apellido=jugador.apellido,
                dni=jugador.dni,
                anioNacimiento=jugador.anioNacimiento,
                idJugador=id_jugador,
            )
        except sqlite3.Error:
            return None

    def link_to_club(self, jc: JugadorClub) -> None:
        cursor = self.conexion.cursor()

        query = "INSERT INTO jugadorClub (idJugador, idClub, fechaDesde) VALUES (?, ?, ?)"
        cursor.execute(query, (jc.id_jugador, jc.id_club, jc.fechaDesde))
        self.conexion.commit()

    def club_activo(self, id_jugador: int) -> Club | None:
        cursor = self.conexion.cursor()

        query = """
        SELECT c.* FROM club c
        JOIN jugadorClub jc ON c.idClub = jc.idClub
        WHERE jc.idJugador = ? AND jc.fechaHasta IS NULL;
        """

        cursor.execute(query, (id_jugador,))
        row = cursor.fetchone()

        if row is None:
            return None

        return Club(
            nombre=row["nombre"],
            idClub=row["idClub"],
        )
