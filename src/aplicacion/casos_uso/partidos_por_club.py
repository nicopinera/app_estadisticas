from aplicacion.dtos.partido_dto import PartidoDTO
from aplicacion.utils import id_persistido
from dominio.repositorios.partido_repositorio import PartidoRepositorio


class ListarPartidosPorClubUseCase:
    def __init__(self, repo: PartidoRepositorio):
        """
        Funcion que permite inicializar el caso de uso de listar los partidos de un club
        Args:
            repo (PartidoRepositorio): Repositorio de partidos
        """
        self.repo = repo

    def ejecutar(self, idClub: int) -> list[PartidoDTO]:
        """
        Funcion que permite listar todos los partidos en los que participo un club (como local o visitante)

        Args:
            idClub (int): ID del club del cual se quieren listar los partidos

        Returns:
            list[PartidoDTO]: Lista de partidos del club. Lista vacia si el club no tiene partidos.
        """
        partidos = self.repo.buscar_por_club(idClub)
        if not partidos:
            return []
        return [
            PartidoDTO(
                idPartido=id_persistido(p.idPartido, "Partido"),
                fecha=p.fecha,
                estadio=p.estadio,
                idCompetencia=p.idCompetencia,
                idClubLocal=p.idClubLocal,
                idClubVisitante=p.idClubVisitante,
            )
            for p in partidos
        ]
