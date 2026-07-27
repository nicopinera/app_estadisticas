import sqlite3
from typing import Optional


from app_estadisticas.src.dominio.entidades import jugador
from app_estadisticas.src.dominio.entidades.partido import JugadorPartido
from dominio.repositorios.juego_repositorio import JuegoRepositorio 
from Infraestructura.persistencia.sqlite_conexion import SqliteConexion

class SqliteJuegoRepositorio(JuegoRepositorio):
    def __init__(self, conexion: SqliteConexion) -> None:
        self.conexion = conexion

    def _row_to_entity(self, row: sqlite3.Row) -> Juego:
        return Juego(
           fecha=row["fecha"],
           estadio=row["estadio"],
           idCompetencia=row["idCompetencia"],
           idClubLocal=row["idClubLocal"],
           idClubVisitante=row["idClubVisitante"],
        )
    def buscar_por_club(self, id_club: int) -> list[Juego]:
        conexion = self.conexion.obtener_conexion()
        cursor = conexion.cursor()

        query = "SELECT * FROM Juego WHERE idClubLocal = ? OR idClubVisitante = ?"
        cursor.execute(query, (id_club, id_club))
        row = cursor.fetchall()
        if row is None:
            return None
        return [self._row_to_entity(row) for row in row]

    def buscar_por_id(self, idJuego: int) -> Juego:
        conexion = self.conexion.obtener_conexion()
        cursor = conexion.cursor()

        query = "SELECT * FROM Juego WHERE idJuego = ?"
        cursor.execute(query, (idJuego,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_entity(row)

    def guardar_partido(self, partido: Juego) -> Juego:
        conexion = self.conexion.obtener_conexion()
        cursor = conexion.cursor()

        if partido.idJuego is None:
            query = "INSERT INTO Juego (fecha, estadio, idCompetencia, idClubLocal, idClubVisitante) VALUES (?, ?, ?, ?, ?)"
            cursor.execute(query, (partido.fecha, partido.estadio, partido.idCompetencia, partido.idClubLocal, partido.idClubVisitante))
            conexion.commit()

            partido.idJuego = cursor.lastrowid
        else: 
            query = "UPDATE Juego SET fecha = ?, estadio = ?, idCompetencia = ?, idClubLocal = ?, idClubVisitante = ? WHERE idJuego = ?"
            cursor.execute(query, (partido.fecha, partido.estadio, partido.idCompetencia, partido.idClubLocal, partido.idClubVisitante, partido.idJuego))
            conexion.commit()
            
        return partido

    def guardar_boxscore(self, jugador_partido: JugadorPartido) -> JugadorPartido:
        conexion = self.conexion.obtener_conexion()
        cursor = conexion.cursor()

        if jugador_partido.idJugadorPartido is None:
            query = "INSERT INTO JugadorPartido (idJugador, idJuego, idClub, minutosJugados, puntos, t2c, t2l, t3c, t3l, t1c, t1l, rebotesDef, rebotesOf, asistencias, recuperos, perdidas, taponesRecibidos, taponesRealizados, faltasRecibidas, FaltasCometidas) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(query, (jugador_partido.idJugador, jugador_partido.idJuego, jugador_partido.idClub, jugador_partido.minutosJugados, jugador_partido.puntos, jugador_partido.t2c, jugador_partido.t2l, jugador_partido.t3c, jugador_partido.t3l, jugador_partido.t1c, jugador_partido.t1l, jugador_partido.rebotesDef, jugador_partido.rebotesOf, jugador_partido.asistencias, jugador_partido.recuperos, jugador_partido.perdidas, jugador_partido.taponesRecibidos, jugador_partido.taponesRealizados, jugador_partido.faltasRecibidas, jugador_partido.FaltasCometidas))
            conexion.commit()

            jugador_partido.idJugadorPartido = cursor.lastrowid
        else:
            query = "UPDATE JugadorPartido SET idJugador = ?, idJuego = ?, idClub = ?, minutosJugados = ?, puntos = ?, t2c = ?, t2l = ?, t3c = ?, t3l = ?, t1c = ?, t1l = ?, rebotesDef = ?, rebotesOf = ?, asistencias = ?, recuperos = ?, perdidas = ?, taponesRecibidos = ?, taponesRealizados = ?, faltasRecibidas = ?, FaltasCometidas = ? WHERE idJugadorPartido = ?"
            cursor.execute(query, (jugador_partido.idJugador, jugador_partido.idJuego, jugador_partido.idClub, jugador_partido.minutosJugados, jugador_partido.puntos, jugador_partido.t2c, jugador_partido.t2l, jugador_partido.t3c, jugador_partido.t3l, jugadorPartidos.t1c,jugadorPartidos.t1l,jugadorPartidos.rebotesDef,jugadorPartidos.rebotesOf,jugadorPartidos.asistencias,jugadorPartidos.recuperos,jugadorPartidos.perdidas,jugadorPartidos.taponesRecibidos,jugadorPartidos.taponesRealizados,jugadorPartidos.faltasRecibidas,jugadorPartidos.FaltasCometidas,jugadorPartidos.idJugadorPartido))
            conexion.commit()

        return JugadorPartido