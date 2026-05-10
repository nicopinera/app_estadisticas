-- Script para cargar datos de prueba a la base de datos
BEGIN TRANSACTION;
-- 1 Usuario
INSERT INTO usuario (nombre, email, contrasenia)
VALUES (
        'juan',
        'salvatierra',
        'juan.salvatierra@gmail.com',
        'contrasenia1234'
    );
-- 2 Clubes
INSERT INTO club (nombre)
VALUES ('Atenas'),
    ('Universitario');
-- 10 Jugadores
INSERT INTO jugador (nombre, apellido, dni, anioNacimiento)
VALUES ('pepe', 'argento', 12351689, 1980),
    ('antonio', 'argentinito', 2354678, 1985),
    ('Pepa', 'arrigoni', 57105234, 1999),
    ('Gabriel', 'batistuta', 14889392, 2001),
    ('LEONEL ANDRES', 'messi', 18948737, 2005),
    ('Sergio', 'aguero', 44637281, 1993),
    ('Julian', 'alvarez', 09836281, 1945),
    ('cristian', 'romero', 83936423, 1998),
    ('Nico', 'otamendi', 01723465, 2000),
    ('nahuel', 'molina', 91872364, 1987);
-- 1 Competencia
INSERT INTO competencia (nombre, anio, tipo)
VALUES ('PROVINCIAL U21', 2026, 'PROVINCIAL');
-- 2 Partidos
INSERT INTO partido (
        fecha,
        estadio,
        idCompetencia,
        idClubLocal,
        idClubVisitante
    )
VALUES ('2026-05-21', 'Cancha Atenas', 1, 1, 2),
    ('2026-06-20', 'Cancha Universitario', 1, 2, 1);
COMMIT;