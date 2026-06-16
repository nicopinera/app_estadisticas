from abc import ABC, abstractmethod


class CompetenciaRepositorio(ABC):
    "Maneja competencia, categoria, inscripcion, listaBuenaFe y jugadorListaBuenaFe"

    @abstractmethod
    def guardar_competencia():
        pass

    @abstractmethod
    def buscar_competencia_por_id():
        pass

    @abstractmethod
    def obtener_todas_competencias():
        pass

    @abstractmethod
    def guardar_categoria():
        pass

    @abstractmethod
    def obtener_categorias():
        pass

    @abstractmethod
    def guardar_inscripcion():
        pass

    @abstractmethod
    def buscar_inscripcion_por_id():
        pass

    @abstractmethod
    def obtener_inscripciones_por_club():
        pass

    @abstractmethod
    def guardar_lista_buena_fe():
        pass

    @abstractmethod
    def obtener_lista_por_inscripcion():
        pass

    @abstractmethod
    def agregar_jugador_lista():
        pass

    @abstractmethod
    def obtener_jugadores_lista():
        pass
