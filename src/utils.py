"""Utilidades compartidas por las distintas capas del proyecto.

Solo funciones puras y sin dependencias del proyecto: este modulo NO debe importar nada de
`infraestructura`, porque tambien lo usan `aplicacion` y la CLI (una capa interna no puede
depender de una externa).
"""

import argparse
import sys
from datetime import datetime
from typing import NoReturn


def id_persistido(valor: int | None, entidad: str) -> int:
    """
    Devuelve el ID de una entidad que ya fue guardada por un repositorio.

    Las entidades declaran su ID como `int | None` porque antes de guardarse todavia no lo tienen. Una
    entidad que devuelve un repositorio siempre deberia traerlo, y los DTOs de salida exigen un `int`.
    Esta funcion deja explicita esa garantia en un solo lugar (y estrecha el tipo para mypy).

    Args:
        valor (int | None): ID de la entidad devuelta por el repositorio.
        entidad (str): Nombre de la entidad, solo para el mensaje de error.

    Raises:
        RuntimeError: Si el ID es None. Indica un bug en el repositorio, no un error del usuario.

    Returns:
        int: El ID de la entidad.
    """
    if valor is None:
        raise RuntimeError(f"El repositorio devolvio {entidad} sin ID asignado")
    return valor


def abortar(mensaje: str) -> NoReturn:
    """
    Termina la CLI mostrando un error amigable (sin traceback) y con codigo de salida 1.

    El mensaje se imprime en stderr (no en stdout) para no mezclarse con la salida normal del comando.

    Args:
        mensaje (str): Descripcion del error para el usuario.
    """
    print(f"Error: {mensaje}", file=sys.stderr)
    sys.exit(1)


def fecha_iso(valor: str) -> str:
    """
    Valida y normaliza una fecha con formato AAAA-MM-DD. Pensada para usarse como `type=` de argparse.

    Las fechas se guardan como texto y el schema las compara como texto (ej. fechaHasta >= fechaDesde),
    por eso un formato inconsistente ("2026-1-5") rompería esas comparaciones: se normaliza a "2026-01-05".

    Args:
        valor (str): Fecha ingresada por el usuario.

    Raises:
        argparse.ArgumentTypeError: Si no es una fecha valida con formato AAAA-MM-DD.

    Returns:
        str: La fecha normalizada como AAAA-MM-DD.
    """
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date().isoformat()
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{valor}' no es una fecha valida, use el formato AAAA-MM-DD") from None
