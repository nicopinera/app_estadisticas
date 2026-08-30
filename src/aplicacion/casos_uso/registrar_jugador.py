from aplicacion.dtos.jugador_dto import CrearJugadorDTO
from dominio.entidades.jugador import Jugador
from dominio.repositorios.jugador_repositorio import JugadorRepositorio


class RegistrarJugadorUseCase:
    def __init__(self, jugador_repo: JugadorRepositorio):
        self.repo = jugador_repo

    def ejecutar(self, datos: CrearJugadorDTO) -> Jugador:
        jug = Jugador(nombre=datos.nombre, apellido=datos.apellido, dni=datos.dni, anioNacimiento=datos.anioNacimiento)

        resultado = self.repo.guardar(jugador=jug)
        if resultado is not None:
            return resultado
        else:
            return None
