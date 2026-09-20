from aplicacion.dtos.club_dto import VincularJugadorClubDTO
from dominio.entidades.jugador import JugadorClub
from dominio.exceptions import ClubNoEncontradoError, JugadorNoEncontradoError, VinculoActivoExistenteError
from dominio.repositorios.club_repositorio import ClubRepositorio
from dominio.repositorios.jugador_repositorio import JugadorRepositorio


class VincularJugadorAClubUseCase:
    def __init__(self, repo_jugador: JugadorRepositorio, repo_club: ClubRepositorio):
        """
        Funcion que permite inicializar el caso de uso de vincular un jugador a un club
        Args:
            repo_jugador (JugadorRepositorio): Repositorio de jugadores
            repo_club (ClubRepositorio): Repositorio de clubes, para verificar que el club exista
        """
        self.repo_jugador = repo_jugador
        self.repo_club = repo_club

    def ejecutar(self, dto: VincularJugadorClubDTO) -> JugadorClub | None:
        """
        Funcion que permite vincular un jugador a un club

        Args:
            dto (VincularJugadorClubDTO): DTO con el jugador, el club y la fecha de inicio del vinculo

        Raises:
            JugadorNoEncontradoError: Si el jugador no existe.
            ClubNoEncontradoError: Si el club no existe.
            VinculoActivoExistenteError: Si el jugador ya tiene un club activo (el mismo u otro).

        Returns:
            JugadorClub | None: El vinculo creado, o None si no se pudo guardar
        """
        if self.repo_jugador.buscar_por_id(dto.idJugador) is None:
            raise JugadorNoEncontradoError(f"No existe un jugador con idJugador={dto.idJugador}")

        if self.repo_club.buscar_por_id(dto.idClub) is None:
            raise ClubNoEncontradoError(f"No existe un club con idClub={dto.idClub}")

        club_activo = self.repo_jugador.club_activo(dto.idJugador)
        if club_activo:
            raise VinculoActivoExistenteError(
                f"El jugador (idJugador={dto.idJugador}), tiene un club activo (idClub={club_activo.idClub})"
            )

        jc_aux = JugadorClub(fechaDesde=dto.fechaDesde, fechaHasta=None, idJugador=dto.idJugador, idClub=dto.idClub)
        return self.repo_jugador.link_to_club(jc_aux)
