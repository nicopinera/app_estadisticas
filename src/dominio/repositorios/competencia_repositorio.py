from abc import ABC, abstractmethod

from dominio.entidades.competencia import (
    Categoria,
    Competencia,
    Inscripcion,
    JugadorListaBuenaFe,
    ListaBuenaFe,
)


class CompetenciaRepositorio(ABC):
    "Maneja competencia, categoria, inscripcion, listaBuenaFe y jugadorListaBuenaFe"

    @abstractmethod
    def guardar_competencia(self, compe: Competencia) -> Competencia:
        "Registra una Competencia"
        pass

    @abstractmethod
    def buscar_competencia_por_id(self, idCompetencia: int) -> Competencia:
        "Busca una Competencia por id"
        pass

    @abstractmethod
    def obtener_todas_competencias(self) -> list[Competencia]:
        "Devuelve todas las competencias existentes"
        pass

    @abstractmethod
    def guardar_categoria(self, cat: Categoria) -> Categoria:
        "Registra una Categoria"
        pass

    @abstractmethod
    def obtener_categorias(self) -> list[Categoria]:
        "Devuelve todas las categorias existentes"
        pass

    @abstractmethod
    def guardar_inscripcion(self, inscripcion: Inscripcion) -> Inscripcion:
        "Guarda una inscripcion"
        pass

    @abstractmethod
    def buscar_inscripcion_por_id(self, idInscripcion: int) -> Inscripcion:
        "Devuelve informacion de una inscripcion por ID"
        pass

    @abstractmethod
    def obtener_inscripciones_por_club(self, idClub: int) -> list[Inscripcion]:
        "Devuelve todas las inscripciones de un club"
        pass

    @abstractmethod
    def guardar_lista_buena_fe(self, listaBF: ListaBuenaFe) -> ListaBuenaFe:
        "Genera una lista de buena fe vacia"
        pass

    @abstractmethod
    def obtener_lista_por_inscripcion(self, idInscripcion: int) -> ListaBuenaFe:
        "Obtiene informacion de la lista de buena fe de una inscripcion"
        pass

    @abstractmethod
    def agregar_jugador_lista(self, idJugador: int, idListaBuenaFe: int) -> JugadorListaBuenaFe:
        "Agrega un jugador a una lista de buena fe"
        pass

    @abstractmethod
    def obtener_jugadores_lista(self, idListaBuenaFe: int) -> list[JugadorListaBuenaFe]:
        "Obtiene todos los jugadores de una lista de buena fe"
        pass
