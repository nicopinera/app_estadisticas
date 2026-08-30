from aplicacion.dtos.club_dto import ClubDTO, CrearClubDTO
from dominio.entidades.club import Club
from dominio.repositorios.club_repositorio import ClubRepositorio


class CrearClubUseCase:
    def __init__(self, repo: ClubRepositorio):
        self.repo = repo

    def ejecutar(self, dto: CrearClubDTO):
        club = Club(nombre=dto.nombre)
        resultado = self.repo.guardar(club=club)
        if resultado is None:
            return None
        else:
            return ClubDTO(idClub=resultado.idClub, nombre=resultado.nombre)
