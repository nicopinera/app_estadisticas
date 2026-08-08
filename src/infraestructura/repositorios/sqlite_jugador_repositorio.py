import sqlite3

from dominio.entidades.club import Club
from dominio.entidades.jugador import Jugador, JugadorClub
from dominio.repositorios.jugador_repositorio import JugadorRepositorio


class SquliteJugadorRepositorio(JugadorRepositorio):
    def __init__(self, conexion: sqlite3.Connection):
        self.conexion = conexion

    def _row_to_entity(self, row: sqlite3.Row) -> Jugador:
        return Jugador(
            nombre=row["nombre"],
            apellido=row["apellido"],
            dni=row["dni"],
            anioNacimiento=row["anioNacimiento"],
            idJugador=row["id_jugador"],
        )

    def buscar_por_id(self, id_jugador: int) -> Jugador | None:
        cursor = self.conexion.cursor()

        query = "SELECT * FROM Jugador WHERE id_jugador = ?"
        cursor.execute(query, (id_jugador,))
        row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_entity(row)

    def buscar_por_dni(self, dni_jugador: int) -> Jugador | None:
        conexion = self.conexion.obtener_conexion()
        cursor = conexion.cursor()

        query = "SELECT * FROM Jugador WHERE dni = ?"
        cursor.execute(query, (dni_jugador,))
        row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_entity(row)

    def buscar_por_club(self, idClub: int) -> list[JugadorClub]:
        conexion = self.conexion.obtener_conexion()
        cursor = conexion.cursor()

        query = "SELECT * FROM JugadorClub WHERE idClub = ?"
        cursor.execute(query, (idClub,))

        rows = cursor.fetchall()
        if not rows:
            return []

        return [
            JugadorClub(
                fechaDesde=row["fechaDesde"],
                fechaHasta=row["fechaHasta"],
                idJugador=row["idJugador"],
                idClub=row["idClub"],
            )
            for row in rows
        ]

    def guardar(
        self, nombre: str, apellido: str, dni: int, anioNacimiento: int
    ) -> Jugador:
        cursor = self.conexion.cursor()

        query = (
            "INSERT INTO Jugador (nombre, apellido, dni, anioNacimiento) "
            "VALUES (?, ?, ?, ?)"
        )
        cursor.execute(query, (nombre, apellido, dni, anioNacimiento))
        self.conexion.commit()
        id_jugador = cursor.lastrowid

        return Jugador(
            nombre=nombre,
            apellido=apellido,
            dni=dni,
            anioNacimiento=anioNacimiento,
            idJugador=id_jugador,
        )

    def link_to_club(self, id_jugador: int, id_club: int, fechaDesde: str) -> None:
        conexion = self.conexion.obtener_conexion()
        cursor = conexion.cursor()

        query = (
            "INSERT INTO JugadorClub (idJugador, idClub, fechaDesde) VALUES (?, ?, ?)"
        )
        cursor.execute(query, (id_jugador, id_club, fechaDesde))
        self.conexion.commit()

    def club_activo(self, id_jugador: int) -> Club | None:
        cursor = self.conexion.cursor()

        query = (
            "SELECT c.* FROM Club c "
            "JOIN JugadorClub jc ON c.idClub = jc.idClub "
            "WHERE jc.idJugador = ? AND jc.fechaHasta IS NULL"
        )
        cursor.execute(query, (id_jugador,))
        row = cursor.fetchone()

        if row is None:
            return None

        return Club(
            nombre=row["nombre"],
            idClub=row["idClub"],
        )
