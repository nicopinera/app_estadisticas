import sqlite3

import pytest

from dominio.entidades.usuario import Usuario
from infraestructura.repositorios.sqlite_usuario_repositorio import (
    SqliteUsuarioRepositorio,
)


def test_buscar_usuario_id(db_conexion):
    us_rep = SqliteUsuarioRepositorio(db_conexion)
    usuario_encontrado = us_rep.encontrar_por_id(1)
    assert usuario_encontrado.nombre == "juan salvatierra"
    assert usuario_encontrado.email == "juan.salvatierra@gmail.com"
    assert usuario_encontrado.pw == """$2b$10$CwTycUXWue0Thq9StjUM0uJ8s6mG1fK0O9Yx8uWb1x1o1t4bm/FKa"""


def test_buscar_usuario_id_inexistente(db_conexion):
    us_rep = SqliteUsuarioRepositorio(db_conexion)
    usuario_encontrado = us_rep.encontrar_por_id(10)
    assert usuario_encontrado is None


def test_buscar_usuario_email(db_conexion):
    us_rep = SqliteUsuarioRepositorio(db_conexion)
    usuario_encontrado = us_rep.encontrar_por_mail("juan.salvatierra@gmail.com")
    assert usuario_encontrado.nombre == "juan salvatierra"
    assert usuario_encontrado.email == "juan.salvatierra@gmail.com"
    assert usuario_encontrado.pw == """$2b$10$CwTycUXWue0Thq9StjUM0uJ8s6mG1fK0O9Yx8uWb1x1o1t4bm/FKa"""


def test_buscar_usuario_email_inexistente(db_conexion):
    us_rep = SqliteUsuarioRepositorio(db_conexion)
    usuario_encontrado = us_rep.encontrar_por_mail("random@gmail.com")
    assert usuario_encontrado is None


def test_guardar_usuario(db_conexion):
    us_rep = SqliteUsuarioRepositorio(db_conexion)
    nombre = "Claudio"
    email = "claudio@gmail.com"
    pw = "123456"
    us_aux = Usuario(nombre=nombre, email=email, pw=pw)
    us_rep.guardar(us_aux)
    us_reg = us_rep.encontrar_por_mail(email=email)
    assert us_reg.email == email
    assert us_reg.pw == pw
    assert us_reg.nombre == nombre


def test_guardar_usuario_con_error(db_conexion):
    us_rep = SqliteUsuarioRepositorio(db_conexion)
    nombre = 10
    email = "claudio@gmail.com"
    pw = "123456"
    with pytest.raises(TypeError):
        us_aux = Usuario(nombre=nombre, email=email, pw=pw)
        u_aux = us_rep.guardar(us_aux=us_aux)

    nombre = "10"
    email = True
    pw = "123456"
    with pytest.raises(TypeError):
        us_aux = Usuario(nombre=nombre, email=email, pw=pw)
        u_aux = us_rep.guardar(us_aux=us_aux)

    nombre = "10"
    email = "True"
    pw = 123456
    with pytest.raises(TypeError):
        us_aux = Usuario(nombre=nombre, email=email, pw=pw)
        u_aux = us_rep.guardar(us_aux=us_aux)
