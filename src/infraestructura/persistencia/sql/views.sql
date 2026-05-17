BEGIN TRANSACTION;
-- Creacion de Vistas
-- Vista 1: Une partido con clubes y competencia (reemplaza IDs por nombres).
create VIEW v_partidos_resumen AS
SELECT p.fecha,
    p.estadio,
    c.nombre AS competencia,
    cl.nombre as clubLocal,
    cv.nombre as clubVisitante
FROM partido AS p
    INNER JOIN competencia AS c ON p.idCompetencia = c.idCompetencia
    INNER JOIN club AS cl ON p.idClubLocal = cl.idCLub
    INNER JOIN club AS cv ON p.idClubVisitante = cv.idClub;
-- Vista 2: Une jugadorPartido con jugador y club (fuente para Pandas).
create VIEW v_boxscore_completo AS
SELECT j.nombre || ' ' || j.apellido as nombre_completo,
    c.nombre as club,
    part.minutosJugados,
    part.puntos,
    part.T2C,
    part.T2L,
    part.T3C,
    part.T3L,
    part.T1C,
    part.T1L,
    part.rebotesDef,
    part.rebotesOf,
    part.asistencias,
    part.recuperos,
    part.perdidas,
    part.taponesRecibidos,
    part.taponesRealizados,
    part.faltasRecibidas,
    part.faltasCometidas
FROM jugadorPartido AS part
    INNER JOIN jugador AS j ON part.idJugador = j.idJugador
    INNER JOIN club AS c ON part.idClub = c.idClub;
-- Vista 3: Acumulados históricos por jugador y año de competencia.
CREATE VIEW IF NOT EXISTS v_jugador_totales_temporada AS
SELECT j.nombre || ' ' || j.apellido AS nombre_completo,
    comp.anio,
    -- Conteo de partidos
    COUNT(jp.idPartido) AS partidos_jugados,
    -- Acumulados ofensivos
    SUM(jp.puntos) AS total_puntos,
    SUM(jp.T2C) AS t2c,
    SUM(jp.T2L) AS t2l,
    SUM(jp.T3C) AS t3c,
    SUM(jp.T3L) AS t3l,
    SUM(jp.T1C) AS t1c,
    SUM(jp.T1L) AS t1l,
    -- Acumulados generales
    SUM(jp.rebotesDef) AS total_rebotes_def,
    SUM(jp.rebotesOf) AS total_rebotes_of,
    SUM(jp.rebotesDef + jp.rebotesOf) AS total_rebotes,
    SUM(jp.asistencias) AS total_asistencias,
    SUM(jp.recuperos) AS total_recuperos,
    SUM(jp.perdidas) AS total_perdidas,
    SUM(jp.taponesRealizados) AS total_tapones_realizados,
    SUM(jp.taponesRecibidos) AS total_tapones_recibidos,
    SUM(jp.faltasCometidas) AS total_faltas_cometidas,
    SUM(jp.faltasRecibidas) AS total_faltas_recibidas,
    CASE
        WHEN SUM(jp.T2L) > 0 THEN ROUND(CAST(SUM(jp.T2C) AS REAL) / SUM(jp.T2L) * 100, 1)
        ELSE 0.0
    END AS porcentaje_t2,
    CASE
        WHEN SUM(jp.T3L) > 0 THEN ROUND(CAST(SUM(jp.T3C) AS REAL) / SUM(jp.T3L) * 100, 1)
        ELSE 0.0
    END AS porcentaje_t3,
    CASE
        WHEN SUM(jp.T1L) > 0 THEN ROUND(CAST(SUM(jp.T1C) AS REAL) / SUM(jp.T1L) * 100, 1)
        ELSE 0.0
    END AS porcentaje_t1
FROM jugadorPartido jp
    INNER JOIN jugador j ON jp.idJugador = j.idJugador
    INNER JOIN partido p ON jp.idPartido = p.idPartido
    INNER JOIN competencia comp ON p.idCompetencia = comp.idCompetencia
GROUP BY j.idJugador,
    comp.anio;
-- Vista 4: Muestra jugadores habilitados por inscripción.
CREATE VIEW v_listas_detalle AS
SELECT i.idInscripcion,
    cl.nombre AS club,
    cat.nombre AS categoria,
    comp.nombre AS competencia,
    j.nombre || ' ' || j.apellido AS jugador
FROM inscripcion i
    INNER JOIN club cl ON i.idClub = cl.idClub
    INNER JOIN categoria cat ON i.idCategoria = cat.idCategoria
    INNER JOIN competencia comp ON i.idCompetencia = comp.idCompetencia
    INNER JOIN listaBuenaFe lbf ON lbf.idInscripcion = i.idInscripcion
    INNER JOIN jugadorListaBuenaFe jlbf ON jlbf.idListaBuenaFe = lbf.idListaBuenaFe
    INNER JOIN jugador j ON jlbf.idJugador = j.idJugador;
COMMIT;