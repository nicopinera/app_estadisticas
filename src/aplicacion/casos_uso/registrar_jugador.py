from aplicacion.dtos.jugador_dto import CrearJugadorDTO, JugadorDTO
from aplicacion.utils import id_persistido
from dominio.entidades.jugador import Jugador
from dominio.repositorios.jugador_repositorio import JugadorRepositorio


class RegistrarJugadorUseCase:
    def __init__(self, jugador_repo: JugadorRepositorio):
        self.repo = jugador_repo

    def ejecutar(self, datos: CrearJugadorDTO) -> JugadorDTO | None:
        """
        Funcion que permite registrar un jugador nuevo

        Args:
            datos (CrearJugadorDTO): DTO con los datos del jugador a registrar

        Raises:
            DNIDuplicadoError: Si ya existe un jugador con ese DNI (lo lanza el repositorio).

        Returns:
            JugadorDTO | None: DTO con el jugador registrado, o None si no se pudo guardar
        """
        jug = Jugador(nombre=datos.nombre, apellido=datos.apellido, dni=datos.dni, anioNacimiento=datos.anioNacimiento)

        resultado = self.repo.guardar(jugador=jug)
        if resultado is None:
            return None
        return JugadorDTO(
            nombre_completo=f"{resultado.nombre} {resultado.apellido}",
            id=id_persistido(resultado.idJugador, "Jugador"),
            anioNacimiento=resultado.anioNacimiento,
        )
