import random

import pytest

from dominio.entidades.partido import JugadorPartido, Partido
from infraestructura.repositorios.sqlite_partido_repositorio import SqlitePartidoRepositorio


def test_buscar_por_club(db_conexion):
    juego_rep = SqlitePartidoRepositorio(db_conexion)
    juego_encontrado = juego_rep.buscar_por_club(1)
    assert juego_encontrado is not None
    assert len(juego_encontrado) > 0


def test_buscar_por_id(db_conexion):
    juego_rep = SqlitePartidoRepositorio(db_conexion)
    juego_encontrado = juego_rep.buscar_por_id(1)
    assert juego_encontrado is not None
    assert juego_encontrado.idPartido == 1


def test_guardar_partido(db_conexion):
    juego_rep = SqlitePartidoRepositorio(db_conexion)
    partido_aux = Partido(
        estadio="Estadio Principal", fecha="2023-01-01", idClubLocal=1, idClubVisitante=2, idCompetencia=1
    )
    nuevo_juego = juego_rep.guardar_partido(partido=partido_aux)
    assert nuevo_juego is not None
    assert nuevo_juego.idPartido is not None
    assert nuevo_juego.fecha == "2023-01-01"

    partido_aux = Partido(
        estadio="Estadio Principal", fecha="2023-01-01", idClubLocal=12, idClubVisitante=2, idCompetencia=1
    )
    nuevo_juego = juego_rep.guardar_partido(partido=partido_aux)
    assert nuevo_juego is None

    partido_aux = Partido(
        estadio="Estadio Principal", fecha="2023-01-01", idClubLocal=1, idClubVisitante=304, idCompetencia=1
    )
    nuevo_juego = juego_rep.guardar_partido(partido=partido_aux)
    assert nuevo_juego is None

    partido_aux = Partido(
        estadio="Estadio Principal", fecha="2023-01-01", idClubLocal=1, idClubVisitante=2, idCompetencia=205
    )
    nuevo_juego = juego_rep.guardar_partido(partido=partido_aux)
    assert nuevo_juego is None


def test_guardar_boxscore(db_conexion):
    juego_rep = SqlitePartidoRepositorio(db_conexion)
    aux_boxscore = JugadorPartido(
        idJugador=1,
        idPartido=2,
        idClub=1,
        minutosJugados=random.randint(0, 40),
        puntos=random.randint(1, 25),
        t2c=random.randint(1, 2),
        t2l=random.randint(5, 10),
        t3c=random.randint(1, 2),
        t3l=random.randint(5, 10),
        t1c=random.randint(1, 2),
        t1l=random.randint(5, 10),
        rebotesDef=4,
        rebotesOf=2,
        asistencias=5,
        recuperos=3,
        perdidas=2,
        taponesRecibidos=1,
        taponesRealizados=2,
        faltasRecibidas=4,
        faltasCometidas=3,
    )
    nuevo_boxscore = juego_rep.guardar_boxscore(boxscore=aux_boxscore)
    assert nuevo_boxscore is not None

    aux_boxscore = JugadorPartido(
        idJugador=40000,
        idPartido=1,
        idClub=1,
        minutosJugados=random.randint(0, 40),
        puntos=random.randint(1, 25),
        t2c=random.randint(1, 2),
        t2l=random.randint(1, 10),
        t3c=random.randint(1, 2),
        t3l=random.randint(1, 10),
        t1c=random.randint(1, 2),
        t1l=random.randint(5, 10),
        rebotesDef=4,
        rebotesOf=2,
        asistencias=5,
        recuperos=3,
        perdidas=2,
        taponesRecibidos=1,
        taponesRealizados=2,
        faltasRecibidas=4,
        faltasCometidas=3,
    )
    nuevo_boxscore = juego_rep.guardar_boxscore(boxscore=aux_boxscore)
    assert nuevo_boxscore is None

    aux_boxscore = JugadorPartido(
        idJugador=1,
        idPartido=300,
        idClub=1,
        minutosJugados=random.randint(0, 40),
        puntos=random.randint(1, 25),
        t2c=random.randint(1, 2),
        t2l=random.randint(5, 10),
        t3c=random.randint(1, 2),
        t3l=random.randint(5, 10),
        t1c=random.randint(1, 2),
        t1l=random.randint(5, 10),
        rebotesDef=4,
        rebotesOf=2,
        asistencias=5,
        recuperos=3,
        perdidas=2,
        taponesRecibidos=1,
        taponesRealizados=2,
        faltasRecibidas=4,
        faltasCometidas=3,
    )

    nuevo_boxscore = juego_rep.guardar_boxscore(boxscore=aux_boxscore)
    assert nuevo_boxscore is None
    aux_boxscore = JugadorPartido(
        idJugador=1,
        idPartido=1,
        idClub=400,
        minutosJugados=random.randint(0, 40),
        puntos=random.randint(1, 25),
        t2c=random.randint(1, 2),
        t2l=random.randint(5, 10),
        t3c=random.randint(1, 2),
        t3l=random.randint(5, 10),
        t1c=random.randint(1, 2),
        t1l=random.randint(5, 10),
        rebotesDef=4,
        rebotesOf=2,
        asistencias=5,
        recuperos=3,
        perdidas=2,
        taponesRecibidos=1,
        taponesRealizados=2,
        faltasRecibidas=4,
        faltasCometidas=3,
    )

    nuevo_boxscore = juego_rep.guardar_boxscore(boxscore=aux_boxscore)
    assert nuevo_boxscore is None
