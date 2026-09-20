from dataclasses import dataclass


@dataclass
class JugadorDTO:  # Sale en RegistrarJugadorUseCase.execute()
    nombre_completo: str
    id: int
    anioNacimiento: int


@dataclass
class CrearJugadorDTO:  # Entra en RegistrasJugadorUseCase.execute
    nombre: str
    apellido: str
    dni: int
    anioNacimiento: int
