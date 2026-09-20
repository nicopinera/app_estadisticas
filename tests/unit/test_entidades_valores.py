"""Tests unitarios de las reglas de VALOR de las entidades (no vacio, rangos) y de sus propiedades calculadas.

`test_entidades.py` cubre los TIPOS incorrectos (TypeError); aca se cubren los valores del tipo correcto pero
invalidos (DatoInvalidoError): un nombre vacio, un DNI negativo, un año imposible.
"""

from datetime import date

import pytest

from dominio.entidades.club import Club
from dominio.entidades.competencia import Categoria, Competencia
from dominio.entidades.jugador import Jugador
from dominio.exceptions import DatoInvalidoError, ErrorDeDominio

ANIO_ACTUAL = date.today().year
JUGADOR_VALIDO = {"nombre": "Manu", "apellido": "Ginobili", "dni": 20111222, "anioNacimiento": 1977}


@pytest.mark.parametrize(
    "clase, validos, campo, valor, fragmento",
    [
        pytest.param(Club, {"nombre": "Atenas"}, "nombre", "", "nombre del club", id="club-nombre-vacio"),
        pytest.param(Club, {"nombre": "Atenas"}, "nombre", "   ", "nombre del club", id="club-nombre-solo-espacios"),
        pytest.param(Jugador, JUGADOR_VALIDO, "nombre", "", "nombre del jugador", id="jugador-nombre-vacio"),
        pytest.param(Jugador, JUGADOR_VALIDO, "apellido", " ", "apellido del jugador", id="jugador-apellido-vacio"),
        pytest.param(Jugador, JUGADOR_VALIDO, "dni", 0, "DNI", id="jugador-dni-cero"),
        pytest.param(Jugador, JUGADOR_VALIDO, "dni", -5, "DNI", id="jugador-dni-negativo"),
        pytest.param(Jugador, JUGADOR_VALIDO, "anioNacimiento", 1900, "nacimiento", id="jugador-nacio-en-1900"),
        pytest.param(Jugador, JUGADOR_VALIDO, "anioNacimiento", 1850, "nacimiento", id="jugador-nacio-en-1850"),
        pytest.param(
            Jugador, JUGADOR_VALIDO, "anioNacimiento", ANIO_ACTUAL + 1, "nacimiento", id="jugador-nace-en-el-futuro"
        ),
        pytest.param(
            Competencia, {"nombre": "Liga", "anio": 2026}, "nombre", "", "competencia", id="competencia-nombre-vacio"
        ),
        pytest.param(Categoria, {"nombre": "U21"}, "nombre", "  ", "categoria", id="categoria-nombre-vacio"),
    ],
)
def test_entidad_con_valor_invalido_lanza_dato_invalido(clase, validos, campo, valor, fragmento):
    with pytest.raises(DatoInvalidoError, match=fragmento):
        clase(**{**validos, campo: valor})


@pytest.mark.parametrize(
    "campo, valor",
    [
        pytest.param("dni", 1, id="dni-minimo"),
        pytest.param("anioNacimiento", 1901, id="primer-año-valido"),
        pytest.param("anioNacimiento", ANIO_ACTUAL, id="nacio-este-año"),
    ],
)
def test_jugador_en_el_limite_es_valido(campo, valor):
    assert Jugador(**{**JUGADOR_VALIDO, campo: valor}) is not None


def test_dato_invalido_es_un_error_de_dominio_y_tambien_un_value_error():
    # Error de dominio: main() la muestra como mensaje. ValueError: el codigo que ya la capturaba sigue funcionando.
    assert issubclass(DatoInvalidoError, ErrorDeDominio)
    assert issubclass(DatoInvalidoError, ValueError)


def test_el_tipo_incorrecto_sigue_siendo_type_error_y_no_dato_invalido():
    # Un tipo incorrecto es un error de programacion (un bug), no un error de negocio del usuario
    with pytest.raises(TypeError):
        Jugador(**{**JUGADOR_VALIDO, "nombre": None})


# ----------------------------------------------------------------------------- propiedades calculadas


def test_jugador_nombre_completo_junta_nombre_y_apellido():
    assert Jugador(**JUGADOR_VALIDO).nombre_completo == "Manu Ginobili"


def test_boxscore_rebotes_totales_suma_defensivos_y_ofensivos(crear_boxscore):
    assert crear_boxscore(rebotesDef=4, rebotesOf=2).rebotes_totales == 6


def test_boxscore_rebotes_totales_sin_rebotes_es_cero(crear_boxscore):
    assert crear_boxscore(rebotesDef=0, rebotesOf=0).rebotes_totales == 0
