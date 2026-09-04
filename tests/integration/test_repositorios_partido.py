import random

import pytest

from dominio.entidades.partido import JugadorPartido, Partido
from infraestructura.repositorios.sqlite_partido_repositorio import SqlitePartidoRepositorio


def test_buscar_por_club(db_conexion):
    """Funcion que Busca partidos por club

    Args:
        db_conexion (): conexion a la base de datos
    """
    juego_rep = SqlitePartidoRepositorio(db_conexion)
    juego_encontrado = juego_rep.buscar_por_club(1)
    assert juego_encontrado is not None
    assert len(juego_encontrado) > 0


def test_buscar_por_id(db_conexion):
    """Funcion que Busca partidos por id

    Args:
        db_conexion (_type_): conexion a la base de datos
    """
    juego_rep = SqlitePartidoRepositorio(db_conexion)
    juego_encontrado = juego_rep.buscar_por_id(1)
    assert juego_encontrado is not None
    assert juego_encontrado.idPartido == 1


def test_guardar_partido(db_conexion):
    """Funcion que guarda partido en la Base de Datos

    Args:
        db_conexion (_type_): Conexion a la base de datos
    """
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
        minutosJugados=20.0,
        puntos=9,
        t2c=2,
        t2l=5,
        t3c=1,
        t3l=5,
        t1c=2,
        t1l=5,
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
        minutosJugados=20.0,
        puntos=9,
        t2c=2,
        t2l=5,
        t3c=1,
        t3l=5,
        t1c=2,
        t1l=5,
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
        minutosJugados=20.0,
        puntos=9,
        t2c=2,
        t2l=5,
        t3c=1,
        t3l=5,
        t1c=2,
        t1l=5,
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
        minutosJugados=20.0,
        puntos=9,
        t2c=2,
        t2l=5,
        t3c=1,
        t3l=5,
        t1c=2,
        t1l=5,
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


def test_save_with_boxscore_rollback_no_deja_partido_huerfano(db_conexion):
    """US-102 AC4: ante un boxscore con FK inválida, la transacción entera se revierte."""
    juego_rep = SqlitePartidoRepositorio(db_conexion)

    partido = Partido(
        estadio="Estadio Test Rollback",
        fecha="2026-01-01",
        idClubLocal=1,
        idClubVisitante=2,
        idCompetencia=1,
    )

    # Fila válida
    fila_ok = JugadorPartido(
        idJugador=1,
        idPartido=0,  # será sobreescrito por save_with_boxscore
        idClub=1,
        minutosJugados=30.0,
        puntos=9,
        t2c=2,
        t2l=5,
        t3c=1,
        t3l=3,
        t1c=2,
        t1l=4,
        rebotesDef=3,
        rebotesOf=1,
        asistencias=2,
        recuperos=1,
        perdidas=1,
        taponesRecibidos=0,
        taponesRealizados=1,
        faltasRecibidas=2,
        faltasCometidas=1,
    )

    # Fila con idJugador inexistente → viola FK → provoca rollback
    fila_invalida = JugadorPartido(
        idJugador=999999,  # FK inválida: jugador no existe
        idPartido=0,
        idClub=1,
        minutosJugados=25.0,
        puntos=4,
        t2c=1,
        t2l=3,
        t3c=0,
        t3l=2,
        t1c=2,
        t1l=4,
        rebotesDef=2,
        rebotesOf=1,
        asistencias=3,
        recuperos=0,
        perdidas=2,
        taponesRecibidos=1,
        taponesRealizados=0,
        faltasRecibidas=1,
        faltasCometidas=2,
    )

    resultado = juego_rep.save_with_boxscore(partido, [fila_ok, fila_invalida])

    # La transacción debe haber fallado → retorna None
    assert resultado is None

    # El partido NO debe haber quedado guardado (sin partido huérfano)
    cursor = db_conexion.cursor()
    cursor.execute("SELECT COUNT(*) FROM partido WHERE fecha = '2026-01-01' AND estadio = 'Estadio Test Rollback'")
    count = cursor.fetchone()[0]
    assert count == 0
