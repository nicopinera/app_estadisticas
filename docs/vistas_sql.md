# Vistas SQL: Simplificando el Análisis de Datos

## 1. ¿Qué es una Vista SQL?

Una **Vista** es, esencialmente, una "tabla virtual". No almacena datos físicamente por sí misma, sino que guarda una consulta `SELECT` predefinida. Cuando consultas una vista, la base de datos ejecuta esa consulta en tiempo real sobre las tablas base.

En nuestro sistema, las vistas son el puente entre los **datos crudos** (puntos, rebotes de un partido) y las **estadísticas útiles** (promedios por temporada, totales históricos).

---

## 2. ¿Por qué usar Vistas en StatsPro Basketball?

### A. Consistencia de Cálculos (DRY - Don't Repeat Yourself)

En lugar de escribir la lógica para sumar puntos en cada parte del código Python, la escribimos una vez en la base de datos.

- _Sin vista:_ Python tiene que pedir todos los partidos y sumar uno por uno.
- _Con vista:_ Python simplemente hace `SELECT * FROM v_jugador_totales`.

### B. Desacoplamiento (Capa de Infraestructura)

Si decidimos cambiar el nombre de una columna en la tabla `jugadorPartido`, solo actualizamos la Vista. El motor de Pandas en Python ni siquiera se enterará, porque sigue leyendo la misma Vista.

### C. Preparación para Pandas

Pandas es excelente procesando datos estructurados. Al usar vistas, le entregamos a Pandas un "DataFrame" ya pre-filtrado y limpio, lo que ahorra memoria y tiempo de CPU en la aplicación local/móvil.

---

## 3. Implementación en SQLite

La sintaxis básica es:

```sql
CREATE VIEW nombre_de_la_vista AS
SELECT columnas
FROM tablas
WHERE condiciones;
```

### Ejemplo Práctico: Totales por Jugador

Para calcular cuántos puntos y tiros lleva un jugador sin tener que sumar manualmente en Python:

```sql
CREATE VIEW v_jugador_totales AS
SELECT
    idJugador,
    COUNT(idPartido) as partidos_jugados,
    SUM(puntos) as total_puntos,
    SUM(T3C) as t3_convertidos,
    SUM(T3L) as t3_lanzados,
    -- Cálculo de porcentaje básico (evitando división por cero)
    CASE
        WHEN SUM(T3L) > 0 THEN ROUND(CAST(SUM(T3C) AS FLOAT) / SUM(T3L) * 100, 2)
        ELSE 0
    END as porcentaje_t3
FROM jugadorPartido
GROUP BY idJugador;
```

---

## 4. Uso desde la Aplicación (Python)

Desde el código, tratamos a la vista exactamente como si fuera una tabla:

```python
# En el repositorio de infraestructura
cursor.execute("SELECT * FROM v_jugador_totales WHERE idJugador = ?", (jugador_id,))
datos = cursor.fetchone()
```

---

## 6. Catálogo de Vistas del Sistema

A continuación se detallan las vistas que implementaremos para alimentar el motor de estadísticas y la interfaz de usuario.

### A. Resumen de Partidos (`v_partidos_resumen`)

Ideal para listados en la UI. Reemplaza los IDs de clubes y competencias por sus nombres reales.

```sql
CREATE VIEW v_partidos_resumen AS
SELECT
    p.idPartido,
    p.fecha,
    p.estadio,
    comp.nombre AS competencia,
    comp.anio,
    cl.nombre AS club_local,
    cv.nombre AS club_visitante
FROM partido p
JOIN competencia comp ON p.idCompetencia = comp.idCompetencia
JOIN club cl ON p.idClubLocal = cl.idClub
JOIN club cv ON p.idClubVisitante = cv.idClub;
```

### B. Box Score Detallado (`v_boxscore_completo`)

Esta vista une la estadística básica con los nombres de los jugadores. Es la fuente principal para el análisis por partido en Pandas.

```sql
CREATE VIEW v_boxscore_completo AS
SELECT
    jp.idPartido,
    j.idJugador,
    j.nombre || ' ' || j.apellido AS nombre_jugador,
    cl.nombre AS nombre_club,
    jp.minutosJugados,
    jp.puntos,
    jp.T2C, jp.T2L,
    jp.T3C, jp.T3L,
    jp.T1C, jp.T1L,
    (jp.rebotesDef + jp.rebotesOf) AS rebotes_totales,
    jp.asistencias,
    jp.recuperos,
    jp.perdidas,
    jp.faltasCometidas
FROM jugadorPartido jp
JOIN jugador j ON jp.idJugador = j.idJugador
JOIN club cl ON jp.idClub = cl.idClub;
```

### C. Acumulados por Temporada (`v_jugador_totales_temporada`)

Agrupa el desempeño de los jugadores por año de competencia. Fundamental para ver la evolución histórica.

```sql
CREATE VIEW v_jugador_totales_temporada AS
SELECT
    j.idJugador,
    j.nombre || ' ' || j.apellido AS nombre_jugador,
    comp.anio,
    COUNT(jp.idPartido) as partidos_jugados,
    SUM(jp.puntos) as total_puntos,
    SUM(jp.T2C) as t2_convertidos,
    SUM(jp.T2L) as t2_lanzados,
    SUM(jp.T3C) as t3_convertidos,
    SUM(jp.T3L) as t3_lanzados,
    SUM(jp.asistencias) as total_asistencias,
    SUM(jp.rebotesDef + jp.rebotesOf) as total_rebotes
FROM jugadorPartido jp
JOIN jugador j ON jp.idJugador = j.idJugador
JOIN partido p ON jp.idPartido = p.idPartido
JOIN competencia comp ON p.idCompetencia = comp.idCompetencia
GROUP BY j.idJugador, comp.anio;
```

### D. Listas de Buena Fe por Inscripción (`v_listas_detalle`)

Permite consultar rápidamente qué jugadores están habilitados para una competencia específica.

```sql
CREATE VIEW v_listas_detalle AS
SELECT
    i.idInscripcion,
    cl.nombre AS club,
    cat.nombre AS categoria,
    comp.nombre AS competencia,
    j.nombre || ' ' || j.apellido AS jugador
FROM inscripcion i
JOIN club cl ON i.idClub = cl.idClub
JOIN categoria cat ON i.idCategoria = cat.idCategoria
JOIN competencia comp ON i.idCompetencia = comp.idCompetencia
JOIN listaBuenaFe lbf ON lbf.idInscripcion = i.idInscripcion
JOIN jugadorListaBuenaFe jlbf ON jlbf.idListaBuenaFe = lbf.idListaBuenaFe
JOIN jugador j ON jlbf.idJugador = j.idJugador;
```
