from aplicacion.dtos.club_dto import VincularJugadorClubDTO
from dominio.entidades.jugador import JugadorClub
from dominio.exceptions import VinculoActivoExistenteError
from dominio.repositorios.jugador_repositorio import JugadorRepositorio


class VincularJugadorAClubUseCase:
    def __init__(self, repo_jugador: JugadorRepositorio):
        self.repo_jugador = repo_jugador

    def ejecutar(self, dto: VincularJugadorClubDTO):
        "Primero verifico si tiene algun club activo"
        club_activo = self.repo_jugador.club_activo(dto.idJugador)

        "Si tiene un club activo, tiro un VinculoActivoExistenteError"
        if club_activo:
            raise VinculoActivoExistenteError(
                f"El jugador (idJugador={dto.idJugador}), tiene un club activo (idClub={club_activo.idClub})"
            )
        jc_aux = JugadorClub(fechaDesde=dto.fechaDesde, fechaHasta=None, idJugador=dto.idJugador, idClub=dto.idClub)
        return self.repo_jugador.link_to_club(jc_aux)
