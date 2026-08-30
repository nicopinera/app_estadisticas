from aplicacion.dtos.club_dto import ClubDTO
from dominio.entidades.club import UsuarioClub
from dominio.repositorios.club_repositorio import ClubRepositorio


class ListarClubesUsuarioUseCase:
    def __init__(self, repo: ClubRepositorio):
        self.repo = repo

    def ejecutar(self, idUsuario: int) -> list[ClubDTO] | None:
        lista_club = self.repo.buscar_por_id_usuario(idUsuario)
        if lista_club:
            lc = []
            for c in lista_club:
                aux = ClubDTO(idClub=c.idClub, nombre=c.nombre)
                lc.append(aux)
            return lc
        else:
            return None
