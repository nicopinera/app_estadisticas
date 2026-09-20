from aplicacion.dtos.competencia_dto import CompetenciaDTO, CrearCompetenciaDTO
from aplicacion.utils import id_persistido
from dominio.entidades.competencia import Competencia
from dominio.repositorios.competencia_repositorio import CompetenciaRepositorio


class CrearCompetenciaUseCase:
    def __init__(self, repo: CompetenciaRepositorio):
        """
        Funcion que permite inicializar el caso de uso de crear una competencia
        Args:
            repo (CompetenciaRepositorio): Repositorio de competencias
        """
        self.repo = repo

    def ejecutar(self, dto: CrearCompetenciaDTO) -> CompetenciaDTO | None:
        """
        Funcion que permite crear una competencia en la base de datos

        Args:
            dto (CrearCompetenciaDTO): DTO que contiene la informacion de la competencia a crear

        Raises:
            TypeError: Si algun dato de la competencia tiene un tipo incorrecto (lo lanza la entidad).
            ValueError: Si el año de la competencia no es valido (lo lanza la entidad).

        Returns:
            CompetenciaDTO | None: DTO con la competencia creada, o None si no se pudo guardar
        """
        competencia = Competencia(nombre=dto.nombre, anio=dto.anio, tipo=dto.tipo)
        resultado = self.repo.guardar_competencia(compe=competencia)
        if resultado is None:
            return None
        return CompetenciaDTO(
            idCompetencia=id_persistido(resultado.idCompetencia, "Competencia"),
            nombre=resultado.nombre,
            anio=resultado.anio,
            tipo=resultado.tipo,
        )
