import sqlite3

from dominio.entidades.competencia import Categoria, Competencia, Inscripcion, JugadorListaBuenaFe, ListaBuenaFe
from dominio.repositorios.competencia_repositorio import CompetenciaRepositorio
from infraestructura.logger import get_logger

logger = get_logger(__name__)


class SqliteCompetenciaRepositorio(CompetenciaRepositorio):
    def __init__(self, conexion: sqlite3.Connection):
        self.conexion = conexion

    def _row_to_entity_Competencia(self, row: sqlite3.Row) -> Competencia:
        return Competencia(nombre=row["nombre"], anio=row["anio"], tipo=row["tipo"], idCompetencia=row["idCompetencia"])

    def _row_to_entity_Categoria(self, row: sqlite3.Row) -> Categoria:
        return Categoria(nombre=row["nombre"], idCategoria=row["idCategoria"])

    def _row_to_entity_Inscripciones(self, row: sqlite3.Row) -> Inscripcion:
        return Inscripcion(
            idClub=row["idClub"],
            idCategoria=row["idCategoria"],
            idCompetencia=row["idCompetencia"],
            idInscripcion=row["idInscripcion"],
        )

    def _row_to_entity_ListaBuenaFe(self, row: sqlite3.Row) -> ListaBuenaFe:
        return ListaBuenaFe(
            fechaPresentacion=row["fechaPresentacion"],
            idInscripcion=row["idInscripcion"],
            idListaBuenaFe=row["idListaBuenaFe"],
        )

    def guardar_competencia(self, compe: Competencia) -> Competencia:
        try:
            cursor = self.conexion.cursor()
            query = """
            INSERT INTO competencia (nombre,anio,tipo) VALUES (?,?,?);
            """
            cursor.execute(query, (compe.nombre, compe.anio, compe.tipo))
            self.conexion.commit()
            idCompetencia = cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error al guardar Competencia: {e}", exc_info=True)
            return None

        try:
            return Competencia(nombre=compe.nombre, anio=compe.anio, tipo=compe.tipo, idCompetencia=idCompetencia)
        except TypeError as e:
            logger.critical(f"""Competencia guardado (idCompetencia={idCompetencia})
                                pero no se pudo reconstruir el objeto de retorno: {e}""")
            raise

    def buscar_competencia_por_id(self, idCompetencia: int) -> Competencia:
        cursor = self.conexion.cursor()
        query = """
        SELECT * FROM competencia WHERE idCompetencia = ?;
        """
        cursor.execute(query, (idCompetencia,))
        rows = cursor.fetchone()
        if rows is None:
            return None
        return self._row_to_entity_Competencia(rows)

    def obtener_todas_competencias(self) -> list[Competencia]:
        "Devuelve todas las competencias existentes"
        cursor = self.conexion.cursor()
        query = "SELECT * FROM competencia;"
        cursor.execute(query)
        rows = cursor.fetchall()
        if not rows:
            return None
        lista_competencias = []
        for r in rows:
            aux = self._row_to_entity_Competencia(r)
            lista_competencias.append(aux)
        return lista_competencias

    def guardar_categoria(self, cat: Categoria) -> Categoria:
        "Registra una Categoria"
        try:
            cursor = self.conexion.cursor()
            query = """
            INSERT INTO categoria (nombre) VALUES (?);
            """
            cursor.execute(query, (cat.nombre,))
            self.conexion.commit()
            idCategoria = cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error al guardar Categoria: {e}", exc_info=True)
            return None
        try:
            return Categoria(nombre=cat.nombre, idCategoria=idCategoria)
        except TypeError as e:
            logger.critical(f"""Categoria guardada (idCategoria={idCategoria})
                                pero no se pudo reconstruir el objeto de retorno: {e}""")
            raise

    def obtener_categorias(self) -> list[Categoria]:
        "Devuelve todas las categorias existentes"
        cursor = self.conexion.cursor()
        query = "SELECT * FROM categoria;"
        cursor.execute(query)
        rows = cursor.fetchall()
        if not rows:
            return None
        lista_categorias = []
        for r in rows:
            aux = self._row_to_entity_Categoria(r)
            lista_categorias.append(aux)
        return lista_categorias

    def guardar_inscripcion(self, inscripcion: Inscripcion) -> Inscripcion:
        "Guarda una inscripcion"
        cursor = self.conexion.cursor()
        try:
            query = """
            INSERT INTO inscripcion (idClub,idCategoria,idCompetencia) VALUES (?, ?, ?);
            """
            cursor.execute(query, (inscripcion.idClub, inscripcion.idCategoria, inscripcion.idCompetencia))
            self.conexion.commit()
            idInscripcion = cursor.lastrowid

        except sqlite3.Error as e:
            logger.error(f"Error al guardar inscripcion: {e}", exc_info=True)
            return None
        try:
            return Inscripcion(
                inscripcion.idClub, inscripcion.idCategoria, inscripcion.idCompetencia, idInscripcion=idInscripcion
            )
        except TypeError as e:
            logger.critical(f"""Inscripcion guardada (idCategoria={idInscripcion})
            pero no se pudo reconstruir el objeto de retorno: {e}""")
            raise

    def buscar_inscripcion_por_id(self, idInscripcion: int) -> Inscripcion:
        "Devuelve informacion de una inscripcion por ID"
        cursor = self.conexion.cursor()
        query = "SELECT * FROM inscripcion WHERE idInscripcion = ?;"
        cursor.execute(query, (idInscripcion,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_entity_Inscripciones(row)

    def obtener_inscripciones_por_club(self, idClub: int) -> list[Inscripcion]:
        "Devuelve todas las inscripciones de un club"
        cursor = self.conexion.cursor()

        query = "SELECT * FROM club WHERE idClub = ?;"
        cursor.execute(query, (idClub,))
        row = cursor.fetchall()
        if not row:
            return None

        query = "SELECT * FROM inscripcion WHERE idClub = ?;"
        cursor.execute(query, (idClub,))
        row = cursor.fetchall()
        if not row:
            return None
        lista_inscripciones = []
        for r in row:
            aux = self._row_to_entity_Inscripciones(r)
            lista_inscripciones.append(aux)
        return lista_inscripciones

    def guardar_lista_buena_fe(self, listaBF: ListaBuenaFe) -> ListaBuenaFe:
        "Genera una lista de buena fe vacia"
        cursor = self.conexion.cursor()
        try:
            query = """
            INSERT INTO listaBuenaFe (fechaPresentacion,idInscripcion) VALUES (?,?);
            """
            cursor.execute(query, (listaBF.fechaPresentacion, listaBF.idInscripcion))
            self.conexion.commit()
            idListaBuenaFe = cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error al guardar lista de buena fe: {e}", exc_info=True)
            return None

        try:
            return ListaBuenaFe(
                fechaPresentacion=listaBF.fechaPresentacion,
                idInscripcion=listaBF.idInscripcion,
                idListaBuenaFe=idListaBuenaFe,
            )
        except TypeError as e:
            logger.critical(f"""Lista de buena fe guardada (idListaBuenaFe={idListaBuenaFe})
            pero no se pudo reconstruir el objeto de retorno: {e}""")
            raise

    def obtener_lista_por_inscripcion(self, idInscripcion: int) -> ListaBuenaFe | None:
        "Obtiene informacion de la lista de buena fe de una inscripcion"
        cursor = self.conexion.cursor()

        query = """
        SELECT * FROM inscripcion WHERE idInscripcion = ?;
        """
        cursor.execute(query, (idInscripcion,))
        rows = cursor.fetchone()
        if rows is None:
            return None

        query = """
        SELECT * FROM listaBuenaFe WHERE idInscripcion = ?;
        """
        cursor.execute(query, (idInscripcion,))
        rows = cursor.fetchone()
        if rows is None:
            return None
        return self._row_to_entity_ListaBuenaFe(rows)

    def agregar_jugador_lista(self, idJugador: int, idListaBuenaFe: int) -> JugadorListaBuenaFe | None:
        "Agrega un jugador a una lista de buena fe"
        cursor = self.conexion.cursor()
        try:
            query = """
            INSERT INTO jugadorListaBuenaFe (idJugador, idListaBuenaFe)
            VALUES (?, ?);
            """
            cursor.execute(query, (idJugador, idListaBuenaFe))
            self.conexion.commit()

        except sqlite3.Error as e:
            logger.error(f"Error al agregar jugador a la lista: {e}", exc_info=True)
            return None

        try:
            return JugadorListaBuenaFe(
                idJugador=idJugador,
                idListaBuenaFe=idListaBuenaFe,
            )
        except TypeError as e:
            logger.critical(f"""Jugador agregado a la lista pero no se pudo reconstruir el objeto de retorno: {e}""")
            raise

    def obtener_jugadores_lista(self, idListaBuenaFe: int) -> list[JugadorListaBuenaFe] | None:
        "Obtiene todos los jugadores de una lista de buena fe"
        cursor = self.conexion.cursor()
        query = """
            SELECT *
            FROM jugadorListaBuenaFe
            WHERE idListaBuenaFe = ?;
        """
        cursor.execute(query, (idListaBuenaFe,))
        rows = cursor.fetchall()
        if not rows:
            return None

        return [
            JugadorListaBuenaFe(
                idJugador=row["idJugador"],
                idListaBuenaFe=row["idListaBuenaFe"],
            )
            for row in rows
        ]
