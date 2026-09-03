import sqlite3

from dominio.entidades.club import Club
from dominio.entidades.jugador import Jugador, JugadorClub
from dominio.exceptions import DNIDuplicadoError
from dominio.repositorios.jugador_repositorio import JugadorRepositorio
from infraestructura.logger import get_logger

logger = get_logger(__name__)


class SqliteJugadorRepositorio(JugadorRepositorio):
    def __init__(self, conexion: sqlite3.Connection):
        """ 
        Inicializa el repositorio de jugadores con una conexión a la base de datos SQLite.

        Args:
            conexion (sqlite3.Connection):  Conexion a la base de datos SQLite.
        """
        self.conexion = conexion

    def _row_to_entity(self, row: sqlite3.Row) -> Jugador:
        """Convierte una fila de la base de datos en una entidad Jugador.

        Args:
            row (sqlite3.Row): Fila de la base de datos que representa un jugador.

        Returns:
            Jugador: Entidad Jugador construida a partir de la fila.
        """
        return Jugador(
            nombre=row["nombre"],
            apellido=row["apellido"],
            dni=row["dni"],
            anioNacimiento=row["anioNacimiento"],
            idJugador=row["idJugador"],
        )

    def buscar_por_id(self, id_jugador: int) -> Jugador | None:
        """Funcion que se encarga de buscar un jugador por su ID en la base de datos en el cual fue registrado,
        en el caso de que exista, retorna el jugador, sino retorna None si no se encuentra

        Args:
            id_jugador (int): ID del jugador a buscar.

        Returns:
            Jugador | None: Retorna el jugador encontrado o None si no se encuentra.
        """
        cursor = self.conexion.cursor()

        query = "SELECT * FROM jugador WHERE idJugador = ?"
        cursor.execute(query, (id_jugador,))
        row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_entity(row)

    def buscar_por_dni(self, dni_jugador: int) -> Jugador | None:
        """Funcion que se encarga de buscar un jugador por su DNI en la base de datos en el cual fue registrado,
        en el caso de que exista, retorna el jugador, sino retorna None si no se encuentra
        en la base de datos.
        Args:
            dni_jugador (int): DNI del jugador a buscar.

        Returns:
            Jugador | None: Retorna el jugador encontrado o None si no se encuentra.
        """
        cursor = self.conexion.cursor()

        query = "SELECT * FROM jugador WHERE dni = ?"
        cursor.execute(query, (dni_jugador,))
        row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_entity(row)

    def buscar_por_club(self, idClub: int) -> list[Jugador]:
        """Funcion que se encarga de buscar todos los jugadores de un club en la base de datos.

        Args:
            idClub (int): ID del club del cual se quieren buscar los jugadores.

        Returns:
            list[Jugador]: Lista de jugadores del club.
        """
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
            return []

        resultado = []
        for r in rows:
            j_aux = self._row_to_entity(r)
            resultado.append(j_aux)
        return resultado

    def guardar(self, jugador: Jugador) -> Jugador | None:
        """Funcion que se encarga de guardar un jugador en la BD

        Args:
            jugador (Jugador): Entidad Jugador a guardar.

        Returns:
            Jugador | None: Retorna el jugador guardado con su ID asignado en la BD o None si ocurre un error.
            """
        cursor = self.conexion.cursor()
        try:
            query = """
            SELECT * FROM jugador WHERE dni = ?;
            """
            cursor.execute(query, (jugador.dni,))
            r = cursor.fetchall()
            if r:
                logger.error(f"Ya existe un jugador con DNI {jugador.dni}", exc_info=True)
                raise DNIDuplicadoError(f"Ya existe un jugador con DNI {jugador.dni}")

            query = """
            INSERT INTO jugador (nombre, apellido, dni, anioNacimiento) VALUES (?, ?, ?, ?);
            """
            cursor.execute(
                query,
                (jugador.nombre, jugador.apellido, jugador.dni, jugador.anioNacimiento),
            )
            self.conexion.commit()
            id_jugador = cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error al guardar Jugador: {e}", exc_info=True)
            return None

        try:
            return Jugador(
                nombre=jugador.nombre,
                apellido=jugador.apellido,
                dni=jugador.dni,
                anioNacimiento=jugador.anioNacimiento,
                idJugador=id_jugador,
            )
        except TypeError as e:
            logger.critical(f"""Jugador guardado (idJugador={id_jugador})
                                pero no se pudo reconstruir el objeto de retorno: {e}""")
            raise

    def link_to_club(self, jc: JugadorClub) -> JugadorClub | None:
        """  
        Funcion que se encarga de linkear un jugador con un club en la base de datos.

        Args:
            jc (JugadorClub): Entidad JugadorClub a linkear.

        Returns:
            JugadorClub | None: Retorna el jugador linkeado con el club o None si ocurre un error.
        """
        try:
            cursor = self.conexion.cursor()
            query = "INSERT INTO jugadorClub (idJugador, idClub, fechaDesde) VALUES (?, ?, ?)"
            cursor.execute(query, (jc.idJugador, jc.idClub, jc.fechaDesde))
            self.conexion.commit()
        except sqlite3.Error as e:
            logger.error(f"Error al linkear jugador con club: {e}", exc_info=True)
            return None

        try:
            return JugadorClub(
                fechaDesde=jc.fechaDesde,
                fechaHasta=None,
                idJugador=jc.idJugador,
                idClub=jc.idClub,
            )
        except TypeError as e:
            logger.critical(f"""Jugador linkeado pero no se pudo reconstruir el objeto de retorno: {e}""")
            raise

    def club_activo(self, id_jugador: int) -> Club | None:
        """
        Funcion que se encarga de buscar el club activo de un jugador en la base de datos.
        
        Args:
            id_jugador (int): ID del jugador del cual se quiere buscar el club activo.
        Returns:
            Club | None: Retorna el club activo del jugador o None si no se encuentra.
        """
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

        return Club(nombre=row["nombre"], idClub=row["idClub"])
