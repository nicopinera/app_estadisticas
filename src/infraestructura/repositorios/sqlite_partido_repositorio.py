import sqlite3

from dominio.entidades.partido import JugadorPartido, Partido
from dominio.repositorios.partido_repositorio import PartidoRepositorio
from infraestructura.logger import get_logger

logger = get_logger(__name__)


class SqlitePartidoRepositorio(PartidoRepositorio):
    def __init__(self, conexion: sqlite3.Connection):
        self.conexion = conexion

    def _row_to_entity_Partido(self, row: sqlite3.Row) -> Partido:
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
        return [self._row_to_entity_Partido(row) for row in rows]

    def buscar_por_id(self, idPartido: int) -> Partido | None:
        cursor = self.conexion.cursor()

        query = "SELECT * FROM partido WHERE idPartido = ?"
        cursor.execute(query, (idPartido,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_entity_Partido(row)

    def guardar_partido(self, partido: Partido) -> Partido | None:
        cursor = self.conexion.cursor()
        try:
            query = """
            SELECT * FROM competencia WHERE idCompetencia = ?;
            """
            cursor.execute(query, (partido.idCompetencia,))
            row = cursor.fetchone()
            if row is None:
                return None

            query = """
            SELECT * FROM club WHERE idClub IN (?,?);
            """
            cursor.execute(query, (partido.idClubLocal, partido.idClubVisitante))
            row = cursor.fetchall()
            if not row or len(row) < 2:
                return None
            """
            query = """
            # SELECT * FROM club WHERE idClub = ?;
            """
            cursor.execute(query,(partido.idClubVisitante,))
            row = cursor.fetchone()
            if row is None:
                return None
            """

            query = """
            INSERT INTO partido (fecha, estadio, idCompetencia, idClubLocal, idClubVisitante)
            VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(
                query,
                (partido.fecha, partido.estadio, partido.idCompetencia, partido.idClubLocal, partido.idClubVisitante),
            )
            self.conexion.commit()

            id_partido = cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error al guardar partido: {e}", exc_info=True)
            return None

        try:
            return Partido(
                fecha=partido.fecha,
                estadio=partido.estadio,
                idCompetencia=partido.idCompetencia,
                idClubLocal=partido.idClubLocal,
                idClubVisitante=partido.idClubVisitante,
                idPartido=id_partido,
            )
        except TypeError as e:
            logger.critical(f"""Partido guardado (id_partido={id_partido})
                                pero no se pudo reconstruir el objeto de retorno: {e}""")
            raise

    def guardar_boxscore(self, boxscore: JugadorPartido) -> JugadorPartido | None:
        try:
            cursor = self.conexion.cursor()

            query = """
            SELECT * FROM partido WHERE idPartido = ?;
            """
            cursor.execute(query, (boxscore.idPartido,))
            row = cursor.fetchone()
            if row is None:
                return None

            query = """
            SELECT * FROM jugador WHERE idJugador = ?;
            """
            cursor.execute(query, (boxscore.idJugador,))
            row = cursor.fetchone()
            if row is None:
                return None

            query = """
            SELECT * FROM club WHERE idClub = ?;
            """
            cursor.execute(query, (boxscore.idClub,))
            row = cursor.fetchone()
            if row is None:
                return None

            query = """
                INSERT INTO jugadorPartido
                (idJugador,idPartido,idClub,minutosJugados,puntos,T2C,T2L,T3C,T3L,T1C,T1L,
                rebotesDef,rebotesOf,asistencias,recuperos,perdidas,taponesRecibidos,taponesRealizados,
                faltasRecibidas,faltasCometidas)
                VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
                """
            cursor.execute(
                query,
                (
                    boxscore.idJugador,
                    boxscore.idPartido,
                    boxscore.idClub,
                    boxscore.minutosJugados,
                    boxscore.puntos,
                    boxscore.t2c,
                    boxscore.t2l,
                    boxscore.t3c,
                    boxscore.t3l,
                    boxscore.t1c,
                    boxscore.t1l,
                    boxscore.rebotesDef,
                    boxscore.rebotesOf,
                    boxscore.asistencias,
                    boxscore.recuperos,
                    boxscore.perdidas,
                    boxscore.taponesRecibidos,
                    boxscore.taponesRealizados,
                    boxscore.faltasRecibidas,
                    boxscore.faltasCometidas,
                ),
            )
            self.conexion.commit()
        except sqlite3.Error as e:
            logger.error(f"Error al guardar boxscore: {e}", exc_info=True)
            return None

        try:
            return JugadorPartido(
                idJugador=boxscore.idJugador,
                idPartido=boxscore.idPartido,
                idClub=boxscore.idClub,
                minutosJugados=boxscore.minutosJugados,
                puntos=boxscore.puntos,
                t2c=boxscore.t2c,
                t2l=boxscore.t2l,
                t3c=boxscore.t3c,
                t3l=boxscore.t3l,
                t1c=boxscore.t1c,
                t1l=boxscore.t1l,
                rebotesDef=boxscore.rebotesDef,
                rebotesOf=boxscore.rebotesOf,
                asistencias=boxscore.asistencias,
                recuperos=boxscore.recuperos,
                perdidas=boxscore.perdidas,
                taponesRecibidos=boxscore.taponesRecibidos,
                taponesRealizados=boxscore.taponesRealizados,
                faltasRecibidas=boxscore.faltasRecibidas,
                faltasCometidas=boxscore.faltasCometidas,
            )
        except TypeError as e:
            logger.critical(f"""Boxscore guardado pero no se pudo reconstruir el objeto de retorno: {e}""")
            raise
