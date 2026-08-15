import sqlite3

from dominio.entidades.partido import JugadorPartido, Partido
from dominio.repositorios.partido_repositorio import PartidoRepositorio


class SqlitePartidoRepositorio(PartidoRepositorio):
    def __init__(self, conexion: sqlite3.Connection):
        self.conexion = conexion

    def _row_to_entity(self, row: sqlite3.Row) -> Partido:
        return Partido(
            fecha=row["fecha"],
            estadio=row["estadio"],
            idCompetencia=row["idCompetencia"],
            idClubLocal=row["idClubLocal"],
            idClubVisitante=row["idClubVisitante"],
            idPartido=row["idPartido"],
        )

    def buscar_por_club(self, id_club: int) -> list[Partido] | None:
        cursor = self.conexion.cursor()

        query = "SELECT * FROM partido WHERE idClubLocal = ? OR idClubVisitante = ?"
        cursor.execute(query, (id_club, id_club))
        rows = cursor.fetchall()
        if not rows:
            return None
        return [self._row_to_entity(row) for row in rows]

    def buscar_por_id(self, idPartido: int) -> Partido:
        cursor = self.conexion.cursor()

        query = "SELECT * FROM partido WHERE idPartido = ?"
        cursor.execute(query, (idPartido,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_entity(row)

    def guardar_partido(
        self,
        fecha: str,
        estadio: str,
        idCompetencia: int,
        idClubLocal: int,
        idClubVisitante: int,
    ) -> Partido | None:
        cursor = self.conexion.cursor()
        try:
            query = """
            INSERT INTO Partido (fecha, estadio, idCompetencia, idClubLocal, idClubVisitante)
            VALUES (?, ?, ?, ?, ?)
              """
            cursor.execute(
                query,
                (fecha, estadio, idCompetencia, idClubLocal, idClubVisitante),
            )
            self.conexion.commit()

            id_partido = cursor.lastrowid

            return Partido(
                fecha=fecha,
                estadio=estadio,
                idCompetencia=idCompetencia,
                idClubLocal=idClubLocal,
                idClubVisitante=idClubVisitante,
                idPartido=id_partido,
            )
        except sqlite3.Error as e:
            print(f"\n[ERROR EN GUARDAR PARTIDO]: {e}")
            return None
    def guardar_boxscore(
        self,
        idJugador: int,
        idPartido: int,
        idClub: int,
        minutosJugados: int,
        puntos: int,
        t2c: int,
        t2l: int,
        t3c: int,
        t3l: int,
        t1c: int,
        t1l: int,
        rebotesDef: int,
        rebotesOf: int,
        asistencias: int,
        recuperos: int,
        perdidas: int,
        taponesRecibidos: int,
        taponesRealizados: int,
        faltasRecibidas: int,
        FaltasCometidas: int,
    ) -> JugadorPartido:
        conexion = self.conexion.obtener_conexion()
        cursor = conexion.cursor()

        query = (
            "INSERT INTO JugadorPartido ("
            "idPartido, idJugador, minutosJugados, puntos, t2c, t2l, t3c, t3l, "
            "t1c, t1l, rebotesDef, rebotesOf, asistencias, recuperos, perdidas, "
            "taponesRecibidos, taponesRealizados, faltasRecibidas, FaltasCometidas"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        )
        cursor.execute(
            query,
            (
                idJugador,
                idPartido,
                idClub,
                minutosJugados,
                puntos,
                t2c,
                t2l,
                t3c,
                t3l,
                t1c,
                t1l,
                rebotesDef,
                rebotesOf,
                asistencias,
                recuperos,
                perdidas,
                taponesRecibidos,
                taponesRealizados,
                faltasRecibidas,
                FaltasCometidas,
            ),
        )
        conexion.commit()

        return JugadorPartido(
            idJugador=idJugador,
            idPartido=idPartido,
            idClub=idClub,
            minutosJugados=minutosJugados,
            puntos=puntos,
            t2c=t2c,
            t2l=t2l,
            t3c=t3c,
            t3l=t3l,
            t1c=t1c,
            t1l=t1l,
            rebotesDef=rebotesDef,
            rebotesOf=rebotesOf,
            asistencias=asistencias,
            recuperos=recuperos,
            perdidas=perdidas,
            taponesRecibidos=taponesRecibidos,
            taponesRealizados=taponesRealizados,
            faltasRecibidas=faltasRecibidas,
            faltasCometidas=FaltasCometidas,
        )
