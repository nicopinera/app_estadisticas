from dataclasses import dataclass


@dataclass
class AgregarJugadorListaDTO:
    """Entra a AgregarJugadorAListaBuenaFeUseCase.ejecutar()"""

    idInscripcion: int
    idJugador: int


@dataclass
class JugadorEnListaDTO:
    """Sale de Agregar/QuitarJugador...ListaBuenaFeUseCase: confirma en que lista se habilito o se quito al jugador"""

    idListaBuenaFe: int
    idInscripcion: int
    idJugador: int


@dataclass
class QuitarJugadorListaDTO:
    """Entra a QuitarJugadorDeListaBuenaFeUseCase.ejecutar()"""

    idInscripcion: int
    idJugador: int
