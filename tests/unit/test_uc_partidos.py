"""Tests unitarios del caso de uso de partidos, con un repositorio falso (`unittest.mock`)."""

from unittest.mock import MagicMock

import pytest

from aplicacion.casos_uso.partidos_por_club import ListarPartidosPorClubUseCase
from aplicacion.dtos.partido_dto import PartidoResumenDTO
from dominio.entidades.partido import PartidoResumen
from dominio.repositorios.partido_repositorio import PartidoRepositorio


@pytest.fixture
def repo_partido():
    return MagicMock(spec=PartidoRepositorio)


def test_listar_partidos_muestra_los_nombres_de_la_competencia_y_de_los_clubes(repo_partido):
    repo_partido.resumen_por_club.return_value = [
        PartidoResumen(1, "2026-05-21", "Cancha Atenas", "PROVINCIAL U21", 2026, "Atenas", "Universitario"),
        PartidoResumen(2, "2026-06-20", None, "PROVINCIAL U21", 2026, "Universitario", "Atenas"),
    ]

    resultado = ListarPartidosPorClubUseCase(repo_partido).ejecutar(1)

    assert resultado == [
        PartidoResumenDTO(1, "2026-05-21", "Cancha Atenas", "PROVINCIAL U21", 2026, "Atenas", "Universitario"),
        PartidoResumenDTO(2, "2026-06-20", None, "PROVINCIAL U21", 2026, "Universitario", "Atenas"),
    ]
    repo_partido.resumen_por_club.assert_called_once_with(1)


def test_listar_partidos_sin_partidos_devuelve_lista_vacia(repo_partido):
    repo_partido.resumen_por_club.return_value = []

    assert ListarPartidosPorClubUseCase(repo_partido).ejecutar(1) == []
