import sqlite3

from dominio.entidades.competencia import Categoria, Competencia, Inscripcion, JugadorListaBuenaFe, ListaBuenaFe
from dominio.repositorios.competencia_repositorio import CompetenciaRepositorio
from infraestructura.logger import get_logger

logger = get_logger(__name__)


class SqliteCompetenciaRepositorio(CompetenciaRepositorio):
    def __init__(self, conexion: sqlite3.Connection):
        """Implementamos la interfaz CompetenciaRepositorio, la cual encarga de realizar operaciones CRUD
        (Create, Read, Update, Delete) en la tabla competencia de la base de datos sqlite

        Args:
            conexion (sqlite3.Connection): Conexion a la base de datos SQLite.
        """
        self.conexion = conexion

    def _row_to_entity_Competencia(self, row: sqlite3.Row) -> Competencia:
        """Funcion que se encarga de convertir una fila de la tabla competencia en una entidad Competencia

        Args:
            row (sqlite3.Row): Fila de la tabla competencia de la base de datos.

        Returns:
            Competencia: Entidad Competencia construida a partir de la fila de la base de datos.
        """
        return Competencia(nombre=row["nombre"], anio=row["anio"], tipo=row["tipo"], idCompetencia=row["idCompetencia"])

    def _row_to_entity_Categoria(self, row: sqlite3.Row) -> Categoria:
        """Funcion que se encarga de convertir una fila de la tabla categoria en una entidad Categoria

        Args:
            row (sqlite3.Row): Fila de la tabla categoria de la base de datos.

        Returns:
            Categoria: Entidad Categoria construida a partir de la fila de la base de datos.
        """
        return Categoria(nombre=row["nombre"], idCategoria=row["idCategoria"])

    def _row_to_entity_Inscripciones(self, row: sqlite3.Row) -> Inscripcion:
        """Funcion que se encarga de convertir una fila de la tabla inscripciones en una entidad Inscripcion.

        Args:
            row (sqlite3.Row): Fila de la tabla inscripciones de la base de datos.

        Returns:
            Inscripcion: Entidad Inscripcion construida a partir de la fila de la base de datos.
        """
        return Inscripcion(
            idClub=row["idClub"],
            idCategoria=row["idCategoria"],
            idCompetencia=row["idCompetencia"],
            idInscripcion=row["idInscripcion"],
        )

    def _row_to_entity_ListaBuenaFe(self, row: sqlite3.Row) -> ListaBuenaFe:
        """Funcion que se encarga de convertir una fila de la tabla listaBuenaFe en una entidad ListaBuenaFe

        Args:
            row (sqlite3.Row): Fila de la tabla listaBuenaFe de la base de datos.

        Returns:
            ListaBuenaFe: Entidad ListaBuenaFe construida a partir de la fila de la base de datos.
        """
        return ListaBuenaFe(
            fechaPresentacion=row["fechaPresentacion"],
            idInscripcion=row["idInscripcion"],
            idListaBuenaFe=row["idListaBuenaFe"],
        )

    def guardar_competencia(self, compe: Competencia) -> Competencia | None:
        """Funcion que se encarga de guardar una competencia en la base de datos.

        Args:
            compe (Competencia): Entidad Competencia a guardar.

        Returns:
            Competencia | None: Retorna la competencia guardada con su ID asignado en la BD o None si ocurre un error.
        """
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

    def buscar_competencia_por_id(self, idCompetencia: int) -> Competencia | None:
        """Funcion que se encarga de buscar una competencia por su ID

        Args:
            idCompetencia (int): ID de la competencia a buscar.

        Returns:
            Competencia | None: Retorna la competencia encontrada o None si no se encuentra.
        """
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
        """Funcion que se encarga de obtener todas las competencias existentes en la base de datos

        Returns:
            list[Competencia]: Lista de competencias existentes en la base de datos.
        """

        cursor = self.conexion.cursor()
        query = "SELECT * FROM competencia;"
        cursor.execute(query)
        rows = cursor.fetchall()
        if not rows:
            return []
        lista_competencias = []
        for r in rows:
            aux = self._row_to_entity_Competencia(r)
            lista_competencias.append(aux)
        return lista_competencias

    def guardar_categoria(self, cat: Categoria) -> Categoria | None:
        """Funcion que se encarga de guardar una categoria en la base de datos

        Args:
            cat (Categoria): Entidad Categoria a guardar.

        Returns:
            Categoria | None: Retorna la categoria guardada con su ID asignado en la BD o None si ocurre un error.
        """
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
        """Funcion que se encarga de obtener todas las categorias existentes en la base de datos.

        Returns:
            list[Categoria]: Lista de categorias existentes en la base de datos.
        """
        cursor = self.conexion.cursor()
        query = "SELECT * FROM categoria;"
        cursor.execute(query)
        rows = cursor.fetchall()
        if not rows:
            return []
        lista_categorias = []
        for r in rows:
            aux = self._row_to_entity_Categoria(r)
            lista_categorias.append(aux)
        return lista_categorias

    def guardar_inscripcion(self, inscripcion: Inscripcion) -> Inscripcion | None:
        """Funcion que se encarga de guardar una inscripcion en la base de datos
        Args:
            inscripcion (Inscripcion): Entidad Inscripcion a guardar.

        Returns:
            Inscripcion | None: Retorna la inscripcion guardada con su ID asignado en la BD o None si ocurre un error.
        """
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

    def buscar_inscripcion_por_id(self, idInscripcion: int) -> Inscripcion | None:
        """Funcion que se encarga de devolver informacion de una inscripcion por ID

        Args:
            idInscripcion (int): ID de la inscripcion a buscar.

        Returns:
            Inscripcion | None: Retorna la inscripcion encontrada o None si no se encuentra.
        """
        cursor = self.conexion.cursor()
        query = "SELECT * FROM inscripcion WHERE idInscripcion = ?;"
        cursor.execute(query, (idInscripcion,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_entity_Inscripciones(row)

    def obtener_inscripciones_por_club(self, idClub: int) -> list[Inscripcion]:
        """Funcion que se encarga de devolver todas las inscripciones de un club

        Args:
            idClub (int): ID del club del cual se desean obtener las inscripciones.

        Returns:
            list[Inscripcion]: Lista de inscripciones del club especificado. 
            Retorna una lista vacía si no se encuentran inscripciones.
        """
        cursor = self.conexion.cursor()

        query = "SELECT * FROM club WHERE idClub = ?;"
        cursor.execute(query, (idClub,))
        row = cursor.fetchall()
        if not row:
            return []

        query = "SELECT * FROM inscripcion WHERE idClub = ?;"
        cursor.execute(query, (idClub,))
        row = cursor.fetchall()
        if not row:
            return []
        lista_inscripciones = []
        for r in row:
            aux = self._row_to_entity_Inscripciones(r)
            lista_inscripciones.append(aux)
        return lista_inscripciones

    def guardar_lista_buena_fe(self, listaBF: ListaBuenaFe) -> ListaBuenaFe | None:
        """
        Funcion que se encarga de guardar una lista de buena fe en la base de datos
        Args:
            listaBF (ListaBuenaFe): Entidad ListaBuenaFe a guardar.
        Returns:
            ListaBuenaFe | None: Retorna la lista de buena fe guardada con su ID asignado en la BD 
            o None si ocurre un error.
        """
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
        """Funcion que se encarga de devolver la lista de buena fe de una inscripcion

        Args:
            idInscripcion (int): ID de la inscripcion de la cual se desea obtener la lista de buena fe.

        Returns:
            ListaBuenaFe | None: Retorna la lista de buena fe 
            correspondiente a la inscripcion especificada o None si no se encuentra.
        """

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
        """Funcion que se encarga de agregar un jugador a una lista de buena fe

        Args:
            idJugador (int): ID del jugador a agregar.
            idListaBuenaFe (int): ID de la lista de buena fe a la cual se desea agregar el jugador.

        Returns:
            JugadorListaBuenaFe | None: Retorna la entidad JugadorListaBuenaFe correspondiente al jugador agregado
            a la lista de buena fe o None si ocurre un error.
        """
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

    def obtener_jugadores_lista(self, idListaBuenaFe: int) -> list[JugadorListaBuenaFe]:
        """Funcion que se encarga de devolver todos los jugadores de una lista de buena fe

        Args:
            idListaBuenaFe (int): ID de la lista de buena fe de la cual se desean obtener los jugadores.

        Returns:
            list[JugadorListaBuenaFe]: Lista de entidades JugadorListaBuenaFe 
            correspondientes a los jugadores de la lista de buena fe.
        """
        cursor = self.conexion.cursor()
        query = """
            SELECT *
            FROM jugadorListaBuenaFe
            WHERE idListaBuenaFe = ?;
        """
        cursor.execute(query, (idListaBuenaFe,))
        rows = cursor.fetchall()
        if not rows:
            return []

        return [
            JugadorListaBuenaFe(
                idJugador=row["idJugador"],
                idListaBuenaFe=row["idListaBuenaFe"],
            )
            for row in rows
        ]
