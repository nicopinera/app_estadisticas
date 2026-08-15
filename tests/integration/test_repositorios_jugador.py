import sqlite3

import pytest

from dominio.entidades.jugador import Jugador, JugadorClub
from infraestructura.repositorios.sqlite_jugador_repositorio import ( SqliteJugadorRepositorio )


def test_buscar_por_id(db_conexion):
    jugador_rep = SqliteJugadorRepositorio(db_conexion)
    jugador_encontrado = jugador_rep.buscar_por_id(1)
    assert jugador_encontrado.nombre == "pepe"
    assert jugador_encontrado.apellido == "argento"
    assert jugador_encontrado.dni == 12351689
    assert jugador_encontrado.anioNacimiento == 1980

def test_buscar_por_dni(db_conexion):
    jugador_rep = SqliteJugadorRepositorio(db_conexion)
    jugador_encontrado = jugador_rep.buscar_por_dni(12351689)
    assert jugador_encontrado.nombre == "pepe"
    assert jugador_encontrado.apellido == "argento"
    assert jugador_encontrado.anioNacimiento == 1980

def test_buscar_por_club(db_conexion):
    
    jugador_rep = SqliteJugadorRepositorio(db_conexion)
    #creamos la persona Jugador para vincularla a un determinado club
    nombre = "Carlos"
    apellido = "Mona Jimenez"
    dni = 99887766
    anioNacimiento = 1980

    jugador_aux = Jugador(nombre=nombre, apellido=apellido, dni=dni, anioNacimiento=anioNacimiento)

    jugador_guardado = jugador_rep.guardar(jugador_aux)

    id_club = 1
    jugador_club_aux = JugadorClub(fechaDesde="2023-01-01", fechaHasta=None, idJugador=jugador_guardado.idJugador, idClub=id_club)
    jugador_rep.link_to_club(jugador_club_aux)

    jugadores_encontrados = jugador_rep.buscar_por_club(id_club)

    assert jugadores_encontrados is not None
    assert len(jugadores_encontrados) >= 1
    assert jugadores_encontrados[0].nombre == "Carlos"
    assert jugadores_encontrados[0].apellido == "Mona Jimenez" 
    #esto es para corregir, estuve probando de varias formas y no funciona, es para revisar

def test_guardar(db_conexion):
    jugador_rep = SqliteJugadorRepositorio(db_conexion)
    nombre = "Carlos"
    apellido = "Mona Jimenez"
    dni = 44390785
    anioNacimiento = 1951 
    jugador_aux = Jugador(nombre=nombre, apellido=apellido, dni=dni, anioNacimiento=anioNacimiento)
    jugador_rep.guardar(jugador_aux)
    jugador_reg = jugador_rep.buscar_por_dni(dni)
    assert jugador_reg.nombre == nombre
    assert jugador_reg.apellido == apellido
    assert jugador_reg.anioNacimiento == anioNacimiento
    assert jugador_reg.dni == dni


def test_link_to_club(db_conexion):
    jugador_rep = SqliteJugadorRepositorio(db_conexion)
    jugador_aux = Jugador(nombre="Lionel", apellido="Messi", dni=33016244, anioNacimiento=1987)
    jugador_guardado = jugador_rep.guardar(jugador_aux)

    id_club = 1
    jc = JugadorClub(fechaDesde="2021-08-10", fechaHasta=None, idJugador=jugador_guardado.idJugador, idClub=id_club)
    jugador_rep.link_to_club(jc)

    jugadores_en_club = jugador_rep.buscar_por_club(id_club)
    assert jugadores_en_club is not None
    encontrado = any(j.idJugador == jugador_guardado.idJugador for j in jugadores_en_club)
    assert encontrado is True

def test_club_activo(db_conexion):
    jugador_rep = SqliteJugadorRepositorio(db_conexion)
    jugador_aux = Jugador(nombre="Angel", apellido="Di Maria", dni=34000111, anioNacimiento=1988)
    jugador_guardado = jugador_rep.guardar(jugador_aux)

    id_club = 1
    jc = JugadorClub(fechaDesde="2023-07-01", fechaHasta=None, idJugador=jugador_guardado.idJugador, idClub=id_club)
    jugador_rep.link_to_club(jc)

    club_activo = jugador_rep.club_activo(jugador_guardado.idJugador)
    assert club_activo is not None
    assert club_activo.idClub == id_club