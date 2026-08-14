import pytest


from dominio.entidades.jugador import Jugador
from infraestructura.repositorios.sqlite_jugador_repositorio import SqliteJugadorRepositorio


from dominio.entidades.competencia import Categoria, Competencia, Inscripcion, ListaBuenaFe, JugadorListaBuenaFe
from infraestructura.repositorios.sqlite_competencia_repositorio import ( SqliteCompetenciaRepositorio )


def test_buscar_competencia_por_id(db_conexion):
    comp_rep = SqliteCompetenciaRepositorio(db_conexion)
    comp_encontrada = comp_rep.buscar_competencia_por_id(1)
    assert comp_encontrada.nombre == "PROVINCIAL U21"
    assert comp_encontrada.anio == 2026
    assert comp_encontrada.tipo == "PROVINCIAL"
    
def test_obtener_todas_competencias(db_conexion):
    comp_rep = SqliteCompetenciaRepositorio(db_conexion)
    comp_encontrada = comp_rep.obtener_todas_competencias()
    assert comp_encontrada is not None
    assert len(comp_encontrada) > 0

def test_obtener_categorias(db_conexion):
    cat_rep = SqliteCompetenciaRepositorio(db_conexion)
    cat_encontrada = cat_rep.obtener_categorias()
    assert cat_encontrada is not None
    assert len(cat_encontrada) > 0

def test_buscar_inscripcion_por_id(db_conexion):
    inscripcion_rep = SqliteCompetenciaRepositorio(db_conexion)
    inscripcion_encontrada = inscripcion_rep.buscar_inscripcion_por_id(1)
    assert inscripcion_encontrada is not None
    assert isinstance(inscripcion_encontrada, Inscripcion)
    assert inscripcion_encontrada.idClub == 1
    assert inscripcion_encontrada.idCategoria == 1
    assert inscripcion_encontrada.idCompetencia == 1

def test_obtener_lista_por_inscripcion(db_conexion):
    comp_rep = SqliteCompetenciaRepositorio(db_conexion)
    lista_encontrada = comp_rep.obtener_lista_por_inscripcion(1)
    assert lista_encontrada is not None
    assert len(lista_encontrada) > 0

def test_agregar_jugador_lista(db_conexion):
    comp_rep = SqliteCompetenciaRepositorio(db_conexion)
    jugador_rep = SqliteJugadorRepositorio(db_conexion)

    nuevo_jugador = Jugador(nombre="Facundo", apellido="Campazzo", dni=35123456, anioNacimiento=1991)
    jugador_guardado = jugador_rep.guardar(nuevo_jugador)
    id_lista = 1
    lista_agregada = comp_rep.agregar_jugador_lista(jugador_guardado.idJugador, id_lista)
    assert lista_agregada.idJugador == jugador_guardado.idJugador
    assert lista_agregada.idListaBuenaFe == id_lista

def test_obtener_jugadores_lista(db_conexion):
    comp_rep = SqliteCompetenciaRepositorio(db_conexion)
    jugadores_encontrados = comp_rep.obtener_jugadores_lista(1)
    assert jugadores_encontrados is not None
    assert len(jugadores_encontrados) > 0

def test_guardar_competencia(db_conexion):
    comp_rep = SqliteCompetenciaRepositorio(db_conexion)
    nueva_compe = Competencia(nombre="PROVINCIAL U17", anio=2026, tipo="PROVINCIAL")
    compe_guardada = comp_rep.guardar_competencia(nueva_compe)
    assert compe_guardada is not None
    assert compe_guardada.idCompetencia is not None
    assert compe_guardada.nombre == "PROVINCIAL U17"
    assert compe_guardada.anio == 2026
    assert compe_guardada.tipo == "PROVINCIAL"

def test_guardar_inscripcion(db_conexion):
    comp_rep = SqliteCompetenciaRepositorio(db_conexion)
    nueva_compe = Competencia(nombre="Torneo de Prueba", anio=2026, tipo="PROVINCIAL")
    compe_guardada = comp_rep.guardar_competencia(nueva_compe)

    nueva_inscripcion = Inscripcion(
        idClub=1,
        idCategoria=1,
        idCompetencia=compe_guardada.idCompetencia
    )
    inscripcion_guardada = comp_rep.guardar_inscripcion(nueva_inscripcion)
    assert inscripcion_guardada is not None
    assert inscripcion_guardada.idInscripcion is not None
    assert inscripcion_guardada.idClub == 1
    assert inscripcion_guardada.idCompetencia == compe_guardada.idCompetencia

def test_guardar_categoria(db_conexion):
    comp_rep = SqliteCompetenciaRepositorio(db_conexion)
    nueva_categoria = Categoria(
        idCategoria=2,
        nombre = "U19"
    )
    categoria_guardada = comp_rep.guardar_categoria(nueva_categoria)
    assert categoria_guardada is not None
    assert categoria_guardada.nombre == "U19"
    assert categoria_guardada.idCategoria == 2

def test_obtener_inscripciones_por_club(db_conexion):
    comp_rep = SqliteCompetenciaRepositorio(db_conexion)
    inscripciones = comp_rep.obtener_inscripciones_por_club(1)
    assert inscripciones is not None
    assert len(inscripciones) > 0

def test_guardar_lista_buena_fe(db_conexion): 
    comp_rep = SqliteCompetenciaRepositorio(db_conexion)
    nueva_compe = Competencia(nombre="Torneo Lista Test", anio=2026, tipo="PROVINCIAL")
    compe_guardada = comp_rep.guardar_competencia(nueva_compe)

    nueva_inscripcion = Inscripcion(
        idClub=1, 
        idCategoria=1, 
        idCompetencia=compe_guardada.idCompetencia
    )
    inscripcion_guardada = comp_rep.guardar_inscripcion(nueva_inscripcion)

    nueva_lista = ListaBuenaFe(
        fechaPresentacion="2026-01-02", 
        idInscripcion=inscripcion_guardada.idInscripcion
    )
    lista_guardada = comp_rep.guardar_lista_buena_fe(nueva_lista)

    assert lista_guardada is not None
    assert lista_guardada.idListaBuenaFe is not None
    assert lista_guardada.idInscripcion == inscripcion_guardada.idInscripcion

def obtener_jugadores_lista(db_conexion):
    comp_rep = SqliteCompetenciaRepositorio(db_conexion)
    jugadores_lista = comp_rep.obtener_jugadores_lista(1)

    assert jugadores_lista is not None
    assert len(jugadores_lista) > 0
    assert isinstance(jugadores_lista[0], JugadorListaBuenaFe)