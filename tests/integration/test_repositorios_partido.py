import pytest

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


def guardar_partido(db_conexion):
    juego_rep = SqlitePartidoRepositorio(db_conexion)
    nuevo_juego = juego_rep.guardar_partido(
        fecha="2023-01-01", estadio="Estadio Principal", idCompetencia=1, idClubLocal=1, idClubVisitante=2
    )
    assert nuevo_juego is not None
    assert nuevo_juego.idPartido is not None
    assert nuevo_juego.fecha == "2023-01-01"


def guardar_boxscore(db_conexion):
    juego_rep = SqlitePartidoRepositorio(db_conexion)
    nuevo_boxscore = juego_rep.guardar_boxscore(
        idJugador=1,
        idPartido=1,
        idClub=1,
        minutosJugados=30,
        puntos=25,
        t2c=5,
        t2l=10,
        t3c=3,
        t3l=5,
        t1c=6,
        t1l=8,
        rebotesDef=4,
        rebotesOf=2,
        asistencias=5,
        recuperos=3,
        perdidas=2,
        taponesRecibidos=1,
        taponesRealizados=2,
        faltasRecibidas=4,
        FaltasCometidas=3,
    )
    assert nuevo_boxscore is not None
    assert nuevo_boxscore.idJugador == 1
    assert nuevo_boxscore.idPartido == 1
    assert nuevo_boxscore.idClub == 1
