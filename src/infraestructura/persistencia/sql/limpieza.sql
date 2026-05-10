BEGIN TRANSACTION;
-- Limpieza de tabla usuario
DELETE FROM usuarios
WHERE nombre = 'juan';
-- Limpieza tabla club
DELETE FROM club
WHERE nombre = 'Atenas';
DELETE FROM club
WHERE nombre = 'Universitario';
-- Limpieza tabla Jugadores
DELETE FROM jugador
WHERE idJugador IN (0, 11);
-- Limpieza tabla competencia
DELETE FROM competencia
WHERE nombre = 'PROVINCIAL U21';
-- Limpieza tabla partido
DELETE FROM partido
WHERE fecha = '2026-05-21';
DELETE FROM partido
WHERE fecha = '2026-06-20';
COMMIT;