from collections.abc import Sequence

from tabulate import tabulate


def formatear_tabla(filas: Sequence[Sequence[object]], encabezados: Sequence[str]) -> str:
    """
    Formatea una lista de filas como una tabla de texto para mostrar en la consola.

    Es un wrapper fino de `tabulate`: todos los comandos que listan datos pasan por aca, asi el estilo
    de las tablas se cambia en un solo lugar.

    Args:
        filas (Sequence[Sequence[object]]): Filas de la tabla, una secuencia de valores por fila.
        encabezados (Sequence[str]): Titulos de las columnas.

    Returns:
        str: La tabla lista para imprimir.
    """
    # tabulate no publica tipos (mypy la ve como Any): se declara el tipo del resultado a mano.
    tabla: str = tabulate(filas, headers=encabezados, tablefmt="grid")
    return tabla
