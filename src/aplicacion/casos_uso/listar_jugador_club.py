from aplicacion.dtos.jugador_dto import JugadorDTO
from dominio.repositorios.jugador_repositorio import JugadorRepositorio


class ListarJugadoresClubUseCase:
    def __init__(self, repo: JugadorRepositorio):
        self.repo = repo

    def ejecutar(self, idClub: int):
        lista_jugadores = self.repo.buscar_por_club(idClub=idClub)
        lista_resultado = []
        for j in lista_jugadores:
            aux = JugadorDTO(
                nombre_completo=f"{j.nombre} {j.apellido}", id=j.idJugador, anioNacimiento=j.anioNacimiento
            )
            lista_resultado.append(aux)
        return lista_resultado
