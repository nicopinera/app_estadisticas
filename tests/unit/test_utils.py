"""Tests unitarios de src/utils.py (helpers puros compartidos por todas las capas)."""

import argparse

import pytest

from utils import abortar, fecha_iso, id_persistido


def test_id_persistido_devuelve_el_id():
    assert id_persistido(7, "Club") == 7


def test_id_persistido_none_lanza_runtime_error_con_nombre_de_entidad():
    with pytest.raises(RuntimeError, match="Club"):
        id_persistido(None, "Club")


def test_abortar_termina_con_codigo_1_y_escribe_en_stderr(capsys):
    with pytest.raises(SystemExit) as info:
        abortar("algo salio mal")

    salida = capsys.readouterr()
    assert info.value.code == 1
    assert salida.err == "Error: algo salio mal\n"
    assert salida.out == ""  # nada en stdout: no se mezcla con la salida normal del comando


@pytest.mark.parametrize(
    "ingresado, esperado",
    [
        pytest.param("2026-01-05", "2026-01-05", id="ya-normalizada"),
        pytest.param("2026-1-5", "2026-01-05", id="se-normaliza-sin-ceros"),
        pytest.param("2024-02-29", "2024-02-29", id="anio-bisiesto"),
    ],
)
def test_fecha_iso_valida_y_normaliza(ingresado, esperado):
    assert fecha_iso(ingresado) == esperado


@pytest.mark.parametrize(
    "ingresado",
    [
        pytest.param("31-12-2026", id="orden-dia-mes-anio"),
        pytest.param("2026/01/05", id="separador-barra"),
        pytest.param("2026-02-30", id="dia-inexistente"),
        pytest.param("2026-13-01", id="mes-inexistente"),
        pytest.param("2025-02-29", id="29-feb-en-anio-no-bisiesto"),
        pytest.param("", id="vacia"),
        pytest.param("hola", id="texto"),
    ],
)
def test_fecha_iso_invalida_lanza_argument_type_error(ingresado):
    with pytest.raises(argparse.ArgumentTypeError, match="AAAA-MM-DD"):
        fecha_iso(ingresado)
