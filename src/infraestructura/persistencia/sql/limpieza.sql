BEGIN TRANSACTION;
-- Limpieza de tabla usuario
DELETE FROM usuario
WHERE nombre = 'juan salvatierra';
-- Limpieza tabla partido
DELETE FROM partido
WHERE fecha = '2026-05-21';
DELETE FROM partido
WHERE fecha = '2026-06-20';
COMMIT;
-- Limpieza tabla club
DELETE FROM club
WHERE nombre = 'Atenas';
DELETE FROM club
WHERE nombre = 'Universitario';
-- Limpieza tabla Jugadores
DELETE FROM jugador
WHERE (
        nombre = 'pepe'
        and apellido = 'argento'
    )
    OR (
        nombre = 'antonio'
        and apellido = 'argentinito'
    )
    OR (
        nombre = 'Gabriel'
        and apellido = 'batistuta'
    )
    OR (
        nombre = 'LEONEL ANDRES'
        and apellido = 'messi'
    )
    OR (
        nombre = 'Pepa'
        and apellido = 'arrigoni'
    )
    OR (
        nombre = 'Sergio'
        and apellido = 'aguero'
    )
    OR (
        nombre = 'Julian'
        and apellido = 'alvarez'
    )
    OR (
        nombre = 'cristian'
        and apellido = 'romero'
    )
    OR (
        nombre = 'Nico'
        and apellido = 'otamendi'
    )
    OR (
        nombre = 'nahuel'
        and apellido = 'molina'
    );
-- Limpieza tabla competencia
DELETE FROM competencia
WHERE nombre = 'PROVINCIAL U21';