from abc import ABC, abstractmethod


class CompetenciaRepositorio(ABC):
    "Maneja competencia, categoria, inscripcion, listaBuenaFe y jugadorListaBuenaFe"

    @abstractmethod
    def guardar_competencia(
        self, nombre_competencia: str, anio: int, tipo: str | None
    ) -> None:
        "Registra una Competencia"
        pass

    @abstractmethod
    def buscar_competencia_por_id(self, idCompetencia: int) -> set:
        "Busca una Competencia por id"
        pass

    @abstractmethod
    def obtener_todas_competencias(self) -> list[set]:
        "Devuelve todas las competencias existentes"
        pass

    @abstractmethod
    def guardar_categoria(self, nombre_categoria: str) -> None:
        "Registra una Categoria"
        pass

    @abstractmethod
    def obtener_categorias(self) -> list[set]:
        "Devuelve todas las categorias existentes"
        pass

    @abstractmethod
    def guardar_inscripcion(
        self, idClub: int, idCategoria: int, idCompetencia: int
    ) -> None:
        "Guarda una inscripcion"
        pass

    @abstractmethod
    def buscar_inscripcion_por_id(self, idInscripcion: int) -> set:
        "Devuelve informacion de una inscripcion por ID"
        pass

    @abstractmethod
    def obtener_inscripciones_por_club(self, idClub: int) -> list[set]:
        "Devuelve todas las inscripciones de un club"
        pass

    @abstractmethod
    def guardar_lista_buena_fe(self, fecha: str, idInscripcion: int) -> None:
        "Genera una lista de buena fe vacia"
        pass

    @abstractmethod
    def obtener_lista_por_inscripcion(self, idInscripcion: int) -> set:
        "Obtiene informacion de la lista de buena fe de una inscripcion"
        pass

    @abstractmethod
    def agregar_jugador_lista(self, idJugador: int, idListaBuenaFe: int) -> None:
        "Agrega un jugador a una lista de buena fe"
        pass

    @abstractmethod
    def obtener_jugadores_lista(self, idListaBuenaFe: int) -> list[set]:
        "Obtiene todos los jugadores de una lista de buena fe"
        pass
