import sqlite3

from dominio.entidades.competencia import Categoria, Competencia, Inscripcion, JugadorListaBuenaFe, ListaBuenaFe
from dominio.repositorios.competencia_repositorio import CompetenciaRepositorio


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
            return Competencia(nombre=compe.nombre, anio=compe.anio, tipo=compe.tipo, idCompetencia=idCompetencia)
        except sqlite3.Error:
            return None

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
        cursor = self.conexion.cursor()
        try:
            query = """
            INSERT INTO categoria (nombre) VALUES (?);
            """
            cursor.execute(query, (cat.nombre,))
            self.conexion.commit()
            idCategoria = cursor.lastrowid
            return Categoria(nombre=cat.nombre, idCategoria=idCategoria)
        except sqlite3.Error:
            return None

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
            return Inscripcion(
                inscripcion.idClub, inscripcion.idCategoria, inscripcion.idCompetencia, idInscripcion=idInscripcion
            )
        except sqlite3.Error:
            return None

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
            return ListaBuenaFe(
                fechaPresentacion=listaBF.fechaPresentacion,
                idInscripcion=listaBF.idInscripcion,
                idListaBuenaFe=idListaBuenaFe,
            )
        except sqlite3.Error:
            return None

    def obtener_lista_por_inscripcion(self, idInscripcion: int) -> list[ListaBuenaFe]:
        "Obtiene informacion de la lista de buena fe de una inscripcion"
        cursor = self.conexion.cursor()
        query = """
        SELECT * FROM listaBuenaFe WHERE idInscripcion = ?;
        """
        cursor.execute(query, (idInscripcion,))
        rows = cursor.fetchall()
        if not rows:
            return None
        lista_buena_fe = []
        for r in rows:
            aux = self._row_to_entity_ListaBuenaFe(r)
            lista_buena_fe.append(aux)
        return lista_buena_fe

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

            return JugadorListaBuenaFe(
                idJugador=idJugador,
                idListaBuenaFe=idListaBuenaFe,
            )
        except sqlite3.Error as e:
            print(f"\n[ERROR EN AGREGAR JUGADOR A LISTA]: {e}")
            return None

    def obtener_jugadores_lista(self, idListaBuenaFe: int) -> list[JugadorListaBuenaFe] | None:
        "Obtiene todos los jugadores de una lista de buena fe"
        cursor = self.conexion.cursor()
        try:
            query = """
            SELECT idJugador, idListaBuenaFe
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
        except sqlite3.Error as e:
            print(f"\n[ERROR EN OBTENER JUGADORES DE LISTA]: {e}")
            return None
