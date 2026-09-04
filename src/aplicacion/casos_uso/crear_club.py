from aplicacion.dtos.club_dto import ClubDTO, CrearClubDTO
from dominio.entidades.club import Club
from dominio.repositorios.club_repositorio import ClubRepositorio


class CrearClubUseCase:
    def __init__(self, repo: ClubRepositorio):
        """
        Funcion que permite inicializar el caso de uso de crear un club
        Args:
            repo (ClubRepositorio): _description_
        """
        self.repo = repo

    def ejecutar(self, dto: CrearClubDTO):
        """
        Funcion que permite crear un club en la base de datos

        Args:
            dto (CrearClubDTO): DTO que contiene la informacion del club a crear

        Returns:
            ClubDTO: DTO que contiene la informacion del club creado
        """
        club = Club(nombre=dto.nombre)
        resultado = self.repo.guardar(club=club)
        if resultado is None:
            return None
        else:
            return ClubDTO(idClub=resultado.idClub, nombre=resultado.nombre)
