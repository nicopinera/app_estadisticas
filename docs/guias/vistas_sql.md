# Vistas SQL — Documentación Técnica

> **Fuente de verdad:** ``src/infraestructura/persistencia/sql/views.sql``
> **Última sincronización:** 2026-08-16
> **Versión del schema:** ``schema.sql`` con cláusula ``STRICT``

---

## 1. Introducción y Propósito

### ¿Qué es una vista SQL?

Una **vista** es una consulta ``SELECT`` con nombre, almacenada en la base de datos y tratable como si fuera una tabla. No almacena datos propios: cada vez que se la consulta, SQLite ejecuta la query subyacente en tiempo real sobre las tablas base.

### Rol de las vistas en StatsPro Basketball

Las vistas cumplen una función de **contrato estable entre la base de datos y la capa de análisis**. Actúan como una interfaz pública del modelo relacional hacia:

- **Motor analítico de Pandas:** los DataFrames se construyen directamente desde las vistas. Pandas recibe datos ya estructurados, renombrados y con columnas calculadas listas para graficar.
- **Futura interfaz de usuario:** los listados de partidos, boxscores y habilitados se renderizan desde estas vistas sin lógica adicional de transformación en Python.

```
tablas base (jugadorPartido, partido, jugador, …)
          │
          ▼
  ┌───────────────────┐
  │   vistas SQL      │  ← contrato estable, nombres snake_case, tipos resueltos
  └───────────────────┘
          │
          ▼
pandas.read_sql(…)  /  cursor.execute("SELECT * FROM v_…")
```

**Beneficios clave:**

| Beneficio | Detalle |
|---|---|
| **DRY en cálculos** | Los porcentajes y acumulados se calculan una vez en SQL, no en cada función de Python. |
| **Desacoplamiento** | Cambiar el nombre de una columna interna solo requiere actualizar la vista; Python sigue leyendo el mismo alias snake_case. |
| **Eficiencia** | Pandas recibe el resultado pre-agregado y pre-filtrado; no itera filas crudas en memoria. |
| **Legibilidad** | Las columnas expuestas tienen nombres descriptivos (``total_puntos``, ``porcentaje_t2``) en lugar de los nombres técnicos de la tabla (``puntos``, ``T2C``). |

---

## 2. Catálogo de Vistas Operativas

El sistema dispone de **4 vistas operativas**, creadas en el orden indicado al final de ``views.sql``:

| Vista | Propósito principal |
|---|---|
| ``v_partidos_resumen`` | Listado de partidos con nombres legibles (sin IDs) |
| ``v_boxscore_completo`` | Estadísticas individuales por partido (fuente primaria de Pandas) |
| ``v_jugador_totales_temporada`` | Acumulados y porcentajes por jugador y año de competencia |
| ``v_listas_detalle`` | Jugadores habilitados por inscripción (listas de buena fe) |

---

## 3. Detalle de Cada Vista

---

### 3.1 ``v_partidos_resumen``

#### Descripción funcional

Expone cada partido con los nombres legibles de competencia, club local y club visitante. Elimina la necesidad de hacer JOINs en la capa de aplicación para construir listados de partidos en la UI. Cada fila representa **un partido único**.

#### Tablas involucradas

```
partido  →  competencia  (INNER JOIN por idCompetencia)
partido  →  club (alias cl)  (INNER JOIN por idClubLocal)
partido  →  club (alias cv)  (INNER JOIN por idClubVisitante)
```

#### SQL real (views.sql)

```sql
CREATE VIEW IF NOT EXISTS v_partidos_resumen AS
SELECT
    p.idPartido          AS id_partido,
    p.fecha              AS fecha_partido,
    p.estadio,
    c.nombre             AS competencia,
    c.anio               AS anio_competencia,
    cl.nombre            AS club_local,
    cv.nombre            AS club_visitante
FROM partido AS p
    INNER JOIN competencia AS c  ON p.idCompetencia    = c.idCompetencia
    INNER JOIN club        AS cl ON p.idClubLocal       = cl.idCLub
    INNER JOIN club        AS cv ON p.idClubVisitante   = cv.idClub;
```

#### Columnas expuestas

| Columna | Tipo SQLite | Origen / Cálculo | Descripción |
|---|---|---|---|
| ``id_partido`` | ``INTEGER`` | ``partido.idPartido`` | Clave primaria del partido |
| ``fecha_partido`` | ``TEXT`` | ``partido.fecha`` | Fecha en formato ``YYYY-MM-DD`` |
| ``estadio`` | ``TEXT`` *(nullable)* | ``partido.estadio`` | Nombre del estadio; puede ser ``NULL`` |
| ``competencia`` | ``TEXT`` | ``competencia.nombre`` | Nombre de la competencia |
| ``anio_competencia`` | ``INTEGER`` | ``competencia.anio`` | Año de la competencia (> 1900) |
| ``club_local`` | ``TEXT`` | ``club.nombre`` (alias ``cl``) | Nombre del club que juega de local |
| ``club_visitante`` | ``TEXT`` | ``club.nombre`` (alias ``cv``) | Nombre del club visitante |

> **Nota:** Esta vista no incluye ``idClubLocal`` ni ``idClubVisitante``. Los partidos sin estadio asignado retornan ``NULL`` en la columna ``estadio``.

---

### 3.2 ``v_boxscore_completo``

#### Descripción funcional

Es la **fuente primaria de datos para el análisis con Pandas**. Une la tabla ``jugadorPartido`` con ``jugador`` y ``club`` para exponer toda la estadística individual de un jugador en un partido, reemplazando los IDs por nombres legibles y normalizando los nombres de columna a snake_case. Cada fila representa **la actuación de un jugador en un partido específico**.

#### Tablas involucradas

```
jugadorPartido  →  jugador  (INNER JOIN por idJugador)
jugadorPartido  →  club     (INNER JOIN por idClub)
```

#### SQL real (views.sql)

```sql
CREATE VIEW IF NOT EXISTS v_boxscore_completo AS
SELECT
    part.idPartido          AS id_partido,
    part.idJugador          AS id_jugador,
    part.idClub             AS id_club,
    j.nombre || ' ' || j.apellido  AS nombre_jugador,
    c.nombre                AS nombre_club,
    part.minutosJugados     AS minutos_jugados,
    part.puntos,
    part.T2C                AS t2c,
    part.T2L                AS t2l,
    part.T3C                AS t3c,
    part.T3L                AS t3l,
    part.T1C                AS t1c,
    part.T1L                AS t1l,
    part.rebotesDef         AS rebotes_def,
    part.rebotesOf          AS rebotes_of,
    (part.rebotesDef + part.rebotesOf)  AS rebotes_totales,
    part.asistencias,
    part.recuperos,
    part.perdidas,
    part.taponesRecibidos   AS tapones_recibidos,
    part.taponesRealizados  AS tapones_realizados,
    part.faltasRecibidas    AS faltas_recibidas,
    part.faltasCometidas    AS faltas_cometidas
FROM jugadorPartido AS part
    INNER JOIN jugador AS j ON part.idJugador = j.idJugador
    INNER JOIN club    AS c ON part.idClub    = c.idClub;
```

#### Columnas expuestas

| Columna | Tipo SQLite | Origen / Cálculo | Descripción |
|---|---|---|---|
| ``id_partido`` | ``INTEGER`` | ``jugadorPartido.idPartido`` | FK al partido |
| ``id_jugador`` | ``INTEGER`` | ``jugadorPartido.idJugador`` | FK al jugador |
| ``id_club`` | ``INTEGER`` | ``jugadorPartido.idClub`` | FK al club con el que jugó |
| ``nombre_jugador`` | ``TEXT`` | ``nombre \|\| ' ' \|\| apellido`` | Nombre completo concatenado |
| ``nombre_club`` | ``TEXT`` | ``club.nombre`` | Nombre del club |
| ``minutos_jugados`` | ``REAL`` | ``jugadorPartido.minutosJugados`` | Entre 0 y 48 |
| ``puntos`` | ``INTEGER`` | ``jugadorPartido.puntos`` | Puntos totales anotados |
| ``t2c`` | ``INTEGER`` | ``jugadorPartido.T2C`` | Tiros de 2 puntos convertidos |
| ``t2l`` | ``INTEGER`` | ``jugadorPartido.T2L`` | Tiros de 2 puntos lanzados |
| ``t3c`` | ``INTEGER`` | ``jugadorPartido.T3C`` | Tiros de 3 puntos convertidos |
| ``t3l`` | ``INTEGER`` | ``jugadorPartido.T3L`` | Tiros de 3 puntos lanzados |
| ``t1c`` | ``INTEGER`` | ``jugadorPartido.T1C`` | Tiros libres convertidos |
| ``t1l`` | ``INTEGER`` | ``jugadorPartido.T1L`` | Tiros libres lanzados |
| ``rebotes_def`` | ``INTEGER`` | ``jugadorPartido.rebotesDef`` | Rebotes defensivos |
| ``rebotes_of`` | ``INTEGER`` | ``jugadorPartido.rebotesOf`` | Rebotes ofensivos |
| ``rebotes_totales`` | ``INTEGER`` | ``rebotesDef + rebotesOf`` | Suma calculada en SQL |
| ``asistencias`` | ``INTEGER`` | ``jugadorPartido.asistencias`` | Asistencias |
| ``recuperos`` | ``INTEGER`` | ``jugadorPartido.recuperos`` | Recuperos de balón |
| ``perdidas`` | ``INTEGER`` | ``jugadorPartido.perdidas`` | Pérdidas de balón |
| ``tapones_recibidos`` | ``INTEGER`` | ``jugadorPartido.taponesRecibidos`` | Tapones recibidos |
| ``tapones_realizados`` | ``INTEGER`` | ``jugadorPartido.taponesRealizados`` | Tapones realizados |
| ``faltas_recibidas`` | ``INTEGER`` | ``jugadorPartido.faltasRecibidas`` | Faltas recibidas |
| ``faltas_cometidas`` | ``INTEGER`` | ``jugadorPartido.faltasCometidas`` | Faltas cometidas |

> **Importante:** Esta vista no incluye porcentajes de tiro. Los porcentajes individuales por partido se calculan en Pandas o se consumen desde ``v_jugador_totales_temporada`` para acumulados.

---

### 3.3 ``v_jugador_totales_temporada``

#### Descripción funcional

Agrega toda la producción estadística de cada jugador **por año de competencia**. Incluye sumas de todas las categorías estadísticas y los tres porcentajes de tiro calculados de forma segura ante divisiones por cero. Cada fila representa **el acumulado de un jugador en un año de competencia**.

#### Tablas involucradas

```
jugadorPartido  →  jugador     (INNER JOIN por idJugador)
jugadorPartido  →  partido     (INNER JOIN por idPartido)
partido         →  competencia (INNER JOIN por idCompetencia)
GROUP BY jugador.idJugador, competencia.anio
```

#### SQL real (views.sql)

```sql
CREATE VIEW IF NOT EXISTS v_jugador_totales_temporada AS
SELECT
    j.nombre || ' ' || j.apellido  AS nombre_jugador,
    comp.anio                      AS anio_competencia,
    COUNT(jp.idPartido)            AS partidos_jugados,
    SUM(jp.puntos)                 AS total_puntos,
    SUM(jp.T2C)                    AS total_t2c,
    SUM(jp.T2L)                    AS total_t2l,
    SUM(jp.T3C)                    AS total_t3c,
    SUM(jp.T3L)                    AS total_t3l,
    SUM(jp.T1C)                    AS total_t1c,
    SUM(jp.T1L)                    AS total_t1l,
    SUM(jp.rebotesDef)             AS total_rebotes_def,
    SUM(jp.rebotesOf)              AS total_rebotes_of,
    SUM(jp.rebotesDef + jp.rebotesOf)  AS total_rebotes,
    SUM(jp.asistencias)            AS total_asistencias,
    SUM(jp.recuperos)              AS total_recuperos,
    SUM(jp.perdidas)               AS total_perdidas,
    SUM(jp.taponesRealizados)      AS total_tapones_realizados,
    SUM(jp.taponesRecibidos)       AS total_tapones_recibidos,
    SUM(jp.faltasCometidas)        AS total_faltas_cometidas,
    SUM(jp.faltasRecibidas)        AS total_faltas_recibidas,
    CASE WHEN SUM(jp.T2L) > 0
        THEN ROUND(CAST(SUM(jp.T2C) AS REAL) / SUM(jp.T2L) * 100, 1)
        ELSE 0.0
    END AS porcentaje_t2,
    CASE WHEN SUM(jp.T3L) > 0
        THEN ROUND(CAST(SUM(jp.T3C) AS REAL) / SUM(jp.T3L) * 100, 1)
        ELSE 0.0
    END AS porcentaje_t3,
    CASE WHEN SUM(jp.T1L) > 0
        THEN ROUND(CAST(SUM(jp.T1C) AS REAL) / SUM(jp.T1L) * 100, 1)
        ELSE 0.0
    END AS porcentaje_t1
FROM jugadorPartido jp
    INNER JOIN jugador     j    ON jp.idJugador    = j.idJugador
    INNER JOIN partido     p    ON jp.idPartido     = p.idPartido
    INNER JOIN competencia comp ON p.idCompetencia  = comp.idCompetencia
GROUP BY j.idJugador, comp.anio;
```

#### Columnas expuestas

| Columna | Tipo SQLite | Origen / Cálculo | Descripción |
|---|---|---|---|
| ``nombre_jugador`` | ``TEXT`` | ``nombre \|\| ' ' \|\| apellido`` | Nombre completo del jugador |
| ``anio_competencia`` | ``INTEGER`` | ``competencia.anio`` | Año de la temporada |
| ``partidos_jugados`` | ``INTEGER`` | ``COUNT(jp.idPartido)`` | Partidos en los que registró actuación |
| ``total_puntos`` | ``INTEGER`` | ``SUM(puntos)`` | Puntos totales acumulados |
| ``total_t2c`` | ``INTEGER`` | ``SUM(T2C)`` | Tiros de 2 convertidos acumulados |
| ``total_t2l`` | ``INTEGER`` | ``SUM(T2L)`` | Tiros de 2 lanzados acumulados |
| ``total_t3c`` | ``INTEGER`` | ``SUM(T3C)`` | Tiros de 3 convertidos acumulados |
| ``total_t3l`` | ``INTEGER`` | ``SUM(T3L)`` | Tiros de 3 lanzados acumulados |
| ``total_t1c`` | ``INTEGER`` | ``SUM(T1C)`` | Tiros libres convertidos acumulados |
| ``total_t1l`` | ``INTEGER`` | ``SUM(T1L)`` | Tiros libres lanzados acumulados |
| ``total_rebotes_def`` | ``INTEGER`` | ``SUM(rebotesDef)`` | Rebotes defensivos acumulados |
| ``total_rebotes_of`` | ``INTEGER`` | ``SUM(rebotesOf)`` | Rebotes ofensivos acumulados |
| ``total_rebotes`` | ``INTEGER`` | ``SUM(rebotesDef + rebotesOf)`` | Total de rebotes (def + of) |
| ``total_asistencias`` | ``INTEGER`` | ``SUM(asistencias)`` | Asistencias acumuladas |
| ``total_recuperos`` | ``INTEGER`` | ``SUM(recuperos)`` | Recuperos acumulados |
| ``total_perdidas`` | ``INTEGER`` | ``SUM(perdidas)`` | Pérdidas acumuladas |
| ``total_tapones_realizados`` | ``INTEGER`` | ``SUM(taponesRealizados)`` | Tapones realizados acumulados |
| ``total_tapones_recibidos`` | ``INTEGER`` | ``SUM(taponesRecibidos)`` | Tapones recibidos acumulados |
| ``total_faltas_cometidas`` | ``INTEGER`` | ``SUM(faltasCometidas)`` | Faltas cometidas acumuladas |
| ``total_faltas_recibidas`` | ``INTEGER`` | ``SUM(faltasRecibidas)`` | Faltas recibidas acumuladas |
| ``porcentaje_t2`` | ``REAL`` | ``CASE WHEN SUM(T2L) > 0 … ELSE 0.0`` | % efectividad tiros de 2 |
| ``porcentaje_t3`` | ``REAL`` | ``CASE WHEN SUM(T3L) > 0 … ELSE 0.0`` | % efectividad tiros de 3 |
| ``porcentaje_t1`` | ``REAL`` | ``CASE WHEN SUM(T1L) > 0 … ELSE 0.0`` | % efectividad tiros libres |

#### Protección ante División por Cero

Los tres porcentajes usan el mismo patrón ``CASE WHEN`` para evitar error de división:

```sql
-- Fórmula genérica aplicada a T2, T3 y T1:
CASE WHEN SUM(lanzados) > 0
    THEN ROUND(CAST(SUM(convertidos) AS REAL) / SUM(lanzados) * 100, 1)
    ELSE 0.0
END AS porcentaje_tX
```

| Elemento | Propósito |
|---|---|
| ``CASE WHEN SUM(T2L) > 0`` | Evita la división por cero cuando el jugador no lanzó |
| ``CAST(SUM(T2C) AS REAL)`` | Fuerza aritmética en punto flotante; sin él: ``2 / 5 = 0`` (división entera) |
| ``* 100`` | Convierte proporción ``[0, 1]`` a porcentaje ``[0, 100]`` |
| ``ROUND(…, 1)`` | Redondea a **1 decimal**: ``40.0``, ``66.7``, ``100.0`` |
| ``ELSE 0.0`` | Retorna ``0.0`` (no ``NULL``) para que Pandas no infiera ``NaN`` |

> **Advertencia:** ``ELSE 0.0`` es una decisión de diseño explícita. Si se necesita distinguir "jugador sin intentos" de "jugador con 0% de efectividad", filtrar por ``total_t2l > 0`` antes del análisis en Pandas.

---

### 3.4 ``v_listas_detalle``

#### Descripción funcional

Recorre la cadena completa de habilitación: inscripción → lista de buena fe → jugadores de esa lista. Permite verificar qué jugadores están habilitados para competir en una inscripción específica. Cada fila representa **un jugador habilitado en una inscripción a una competencia**.

#### Tablas involucradas

```
inscripcion
  → club              (INNER JOIN por idClub)
  → categoria         (INNER JOIN por idCategoria)
  → competencia       (INNER JOIN por idCompetencia)
  → listaBuenaFe      (INNER JOIN por idInscripcion)
      → jugadorListaBuenaFe  (INNER JOIN por idListaBuenaFe)
          → jugador          (INNER JOIN por idJugador)
```

> **Nota:** La vista usa ``INNER JOIN`` en todos los pasos. Una inscripción sin lista de buena fe, o una lista sin jugadores, no produce filas en esta vista.

#### SQL real (views.sql)

```sql
CREATE VIEW IF NOT EXISTS v_listas_detalle AS
SELECT
    i.idInscripcion                        AS id_inscripcion,
    cl.nombre                              AS nombre_club,
    cat.nombre                             AS nombre_categoria,
    comp.nombre                            AS nombre_competencia,
    j.nombre || ' ' || j.apellido         AS nombre_jugador
FROM inscripcion i
    INNER JOIN club                  cl   ON i.idClub             = cl.idClub
    INNER JOIN categoria             cat  ON i.idCategoria        = cat.idCategoria
    INNER JOIN competencia           comp ON i.idCompetencia      = comp.idCompetencia
    INNER JOIN listaBuenaFe          lbf  ON lbf.idInscripcion    = i.idInscripcion
    INNER JOIN jugadorListaBuenaFe   jlbf ON jlbf.idListaBuenaFe = lbf.idListaBuenaFe
    INNER JOIN jugador               j    ON jlbf.idJugador       = j.idJugador;
```

#### Columnas expuestas

| Columna | Tipo SQLite | Origen / Cálculo | Descripción |
|---|---|---|---|
| ``id_inscripcion`` | ``INTEGER`` | ``inscripcion.idInscripcion`` | Clave de la inscripción; usar como filtro principal |
| ``nombre_club`` | ``TEXT`` | ``club.nombre`` | Nombre del club inscripto |
| ``nombre_categoria`` | ``TEXT`` | ``categoria.nombre`` | Categoría de la inscripción (ej. "U21") |
| ``nombre_competencia`` | ``TEXT`` | ``competencia.nombre`` | Nombre de la competencia |
| ``nombre_jugador`` | ``TEXT`` | ``nombre \|\| ' ' \|\| apellido`` | Nombre completo del jugador habilitado |

---

## 4. Ejemplos de Consumo con Python y Pandas

### 4.1 Lectura con ``pandas.read_sql``

```python
import sqlite3
import pandas as pd

conexion = sqlite3.connect("ruta/a/appbasquet.db")

# ── Boxscore completo de un partido ───────────────────────────────────
id_partido = 1
df_boxscore = pd.read_sql(
    "SELECT * FROM v_boxscore_completo WHERE id_partido = ?",
    conexion,
    params=(id_partido,),
)
print(df_boxscore[["nombre_jugador", "puntos", "t2c", "t2l", "t3c", "t3l", "rebotes_totales"]])

# ── Totales de temporada de un jugador ────────────────────────────────
df_temporada = pd.read_sql(
    """
    SELECT *
    FROM v_jugador_totales_temporada
    WHERE nombre_jugador LIKE ?
    ORDER BY anio_competencia DESC
    """,
    conexion,
    params=("%messi%",),
)
print(df_temporada[["anio_competencia", "partidos_jugados", "total_puntos",
                     "porcentaje_t2", "porcentaje_t3", "porcentaje_t1"]])

# ── Listado de partidos ───────────────────────────────────────────────
df_partidos = pd.read_sql(
    "SELECT * FROM v_partidos_resumen ORDER BY fecha_partido DESC",
    conexion,
)
print(df_partidos[["fecha_partido", "estadio", "club_local", "club_visitante", "competencia"]])

# ── Jugadores habilitados por inscripción ─────────────────────────────
id_inscripcion = 1
df_lista = pd.read_sql(
    "SELECT * FROM v_listas_detalle WHERE id_inscripcion = ?",
    conexion,
    params=(id_inscripcion,),
)
print(df_lista[["nombre_jugador", "nombre_club", "nombre_categoria"]])
```

### 4.2 Lectura con cursor nativo

```python
cursor = conexion.cursor()
cursor.execute(
    """
    SELECT nombre_jugador, total_puntos, porcentaje_t2
    FROM v_jugador_totales_temporada
    WHERE anio_competencia = ?
    """,
    (2026,)
)
for row in cursor.fetchall():
    print(f"{row['nombre_jugador']}: {row['total_puntos']} pts | %T2: {row['porcentaje_t2']}")
```

> **Tip:** Siempre pasar parámetros como **tupla** ``(valor,)`` — la coma final es obligatoria. Un escalar suelto ``params=id_partido`` hace que ``read_sql`` itere los dígitos del entero y genera error.

---

## 5. Discrepancias Corregidas respecto a la Versión Anterior

| Vista | Discrepancia anterior | Valor real en views.sql |
|---|---|---|
| ``v_partidos_resumen`` | Columna ``idPartido`` (camelCase) | ``id_partido`` |
| ``v_partidos_resumen`` | Columna ``fecha`` | ``fecha_partido`` |
| ``v_partidos_resumen`` | Columna ``anio`` | ``anio_competencia`` |
| ``v_partidos_resumen`` | SQL usaba ``JOIN`` simple | ``INNER JOIN`` |
| ``v_boxscore_completo`` | Columnas ``T2C``, ``T2L`` sin alias | ``t2c``, ``t2l`` (snake_case) |
| ``v_boxscore_completo`` | Columna ``minutosJugados`` | ``minutos_jugados`` |
| ``v_boxscore_completo`` | ``rebotesDef``, ``rebotesOf`` omitidos | ``rebotes_def``, ``rebotes_of`` presentes |
| ``v_boxscore_completo`` | Columnas de tapones y faltas omitidas | Todas presentes con alias snake_case |
| ``v_boxscore_completo`` | ``id_jugador`` e ``id_club`` no expuestos | Sí expuestos en la vista real |
| ``v_jugador_totales_temporada`` | Alias ``t2_convertidos``, ``t2_lanzados`` | ``total_t2c``, ``total_t2l`` |
| ``v_jugador_totales_temporada`` | ``idJugador`` en SELECT | No existe: solo ``nombre_jugador`` |
| ``v_jugador_totales_temporada`` | ``anio`` como alias | ``anio_competencia`` |
| ``v_jugador_totales_temporada`` | 10 columnas en el doc | 23 columnas en la vista real |
| ``v_jugador_totales_temporada`` | ``ROUND(…, 2)`` (2 decimales) | ``ROUND(…, 1)`` (1 decimal) |
| ``v_jugador_totales_temporada`` | ``ELSE 0`` (integer) | ``ELSE 0.0`` (real) |
| ``v_listas_detalle`` | Columna ``club`` | ``nombre_club`` |
| ``v_listas_detalle`` | Columna ``categoria`` | ``nombre_categoria`` |
| ``v_listas_detalle`` | Columna ``competencia`` | ``nombre_competencia`` |
| ``v_listas_detalle`` | Columna ``jugador`` | ``nombre_jugador`` |
| ``v_listas_detalle`` | Columna ``idInscripcion`` (camelCase) | ``id_inscripcion`` |
| Todas | SQL hipotético/borrador en el documento | SQL copiado verbatim de ``views.sql`` |
