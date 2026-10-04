from aplicacion.dtos.club_dto import ClubDTO, CrearClubDTO
from dominio.entidades.club import Club
from dominio.repositorios.club_repositorio import ClubRepositorio
from utils import id_persistido


class CrearClubUseCase:
    def __init__(self, repo: ClubRepositorio):
        """
        Funcion que permite inicializar el caso de uso de crear un club
        Args:
            repo (ClubRepositorio): Repositorio de clubes
        """
        self.repo = repo

    def ejecutar(self, dto: CrearClubDTO) -> ClubDTO | None:
        """
        Funcion que permite crear un club en la base de datos

        Args:
            dto (CrearClubDTO): DTO que contiene la informacion del club a crear

        Returns:
            ClubDTO | None: DTO con el club creado, o None si no se pudo guardar
        """
        club = Club(nombre=dto.nombre)
        resultado = self.repo.guardar(club=club)
        if resultado is None:
            return None
        return ClubDTO(idClub=id_persistido(resultado.idClub, "Club"), nombre=resultado.nombre)
