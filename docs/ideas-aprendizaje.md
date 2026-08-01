# Ideas de servicios/funcionalidades chicas para aprender

> Propuestas puntuales, no demasiado complejas, pensadas como ejercicios de aprendizaje sobre la
> marcha del proyecto — no reemplazan al roadmap del PRD, son "side quests" chicas que enseñan un
> concepto concreto de Python y encajan naturalmente en algún punto de la arquitectura ya
> definida. Ninguna tiene código acá a propósito — son propuestas para que las implementen
> ustedes.

## 1. Decorador de reintento con backoff

**Qué es:** una función que envuelve a otra y, si falla, la reintenta automáticamente con espera
creciente (1s, 2s, 4s...) en vez de fallar directo. Útil para operaciones de I/O que pueden fallar
transitoriamente (leer un Excel bloqueado por otro proceso, escribir a disco cuando el antivirus
está escaneando, etc.).

**Por qué es un buen ejercicio:** enseña **decoradores** de Python (`@mi_decorador` arriba de una
función), que es una herramienta que se usa todo el tiempo en frameworks reales (Flask, pytest,
FastAPI la usan constantemente) y que cuesta entender la primera vez. También es la misma idea de
backoff exponencial que aparece en sistemas distribuidos reales (la vimos en detalle en otro
proyecto con MQTT/reconexión de red).

**Dónde encajaría:** en `infraestructura/ingest/` (Hito 2, US-201), envolviendo la lectura del
Excel de Ges Deportivo — si el archivo está momentáneamente bloqueado (por ejemplo, todavía
abierto en Excel), reintenta un par de veces antes de fallar.

## 2. Cache simple en memoria para consultas de solo lectura

**Qué es:** guardar en memoria (un diccionario, o usando `functools.lru_cache`) el resultado de
una consulta a una vista SQL que no cambia seguido dentro de la misma ejecución del programa —
por ejemplo, la lista de competencias o categorías, que rara vez cambia mientras el usuario está
cargando un partido.

**Por qué es un buen ejercicio:** enseña **memoización** y, más importante, cuándo *no* usarla —
el desafío real de cualquier cache no es guardar el dato, es saber cuándo invalidarlo (¿qué pasa
si el usuario crea una competencia nueva mientras el cache todavía tiene la lista vieja?). Es una
introducción liviana a un problema que en sistemas más grandes se vuelve mucho más difícil.

**Dónde encajaría:** en la capa de infraestructura, como un wrapper opcional alrededor de
`obtener_categorias()`/`obtener_todas_competencias()` del futuro
`SqliteCompetenciaRepositorio` — nunca en el dominio, porque el dominio no debería saber que
existe un cache.

## 3. Exportador a CSV de cualquier vista SQL

**Qué es:** una función chica que toma el nombre de una vista (`v_jugador_totales_temporada`, por
ejemplo) y la vuelca a un archivo `.csv`, reutilizando `pandas.read_sql()` +
`DataFrame.to_csv()`.

**Por qué es un buen ejercicio:** es la introducción más suave posible a Pandas — antes de meterse
con las fórmulas estadísticas más elaboradas de la US-202 (eFG%, EFF, PPP), esto ya te obliga a
practicar el patrón básico "SQL → DataFrame → algo útil" que vas a repetir todo el Hito 2.

**Dónde encajaría:** `infraestructura/analytics/`, como una utilidad chica separada de
`formulas.py` (que según el PRD debe quedar 100% libre de I/O — el exportador si necesita tocar
disco, así que va aparte).

## 4. Loader de configuración por variables de entorno

Este es el que más se amplió a pedido: cómo funciona, qué configuraciones incluiría, y cómo se
conecta con el empaquetado final del Hito 4.

### Cómo funciona

Hoy, `config/rutas.py` calcula rutas relativas al proyecto (dónde está `schema.sql`, dónde va el
`.db`, dónde van los logs) — todo eso está bien porque son ubicaciones que **no dependen del
entorno**, siempre son "relativas a donde vive el código". Un **loader de configuración** es otra
cosa: resuelve valores que **sí** cambian según el entorno (desarrollo vs. testing vs. la
computadora del usuario final) — por ejemplo, el nivel de logging, o si se debe usar una DB en
memoria en vez del archivo real.

El patrón típico en Python:

1. Un archivo `.env` en la raíz del proyecto (con formato `CLAVE=valor` por línea) — **nunca se
   versiona** (va en `.gitignore`), porque puede tener secretos o valores específicos de la
   máquina de cada desarrollador.
2. Un `.env.example` **sí versionado**, con las mismas claves pero valores de ejemplo/vacíos —
   sirve de plantilla para que cualquiera que clone el repo sepa qué variables tiene que definir.
3. La librería `python-dotenv` lee el `.env` al arrancar el programa y carga esas claves a
   `os.environ` (las variables de entorno del proceso).
4. Un módulo (podría llamarse `config/settings.py`) es el **único** lugar del código que llama
   `os.getenv("CLAVE", valor_por_defecto)` — expone esos valores como constantes o atributos de
   una clase `Settings`. El resto de la aplicación nunca llama `os.getenv` directamente; le pide
   el valor a `Settings`. Esto es importante: si mañana cambia *de dónde* viene la configuración
   (ver el punto de empaquetado más abajo), solo se toca `Settings`, nada más en el proyecto se
   entera del cambio.

### Qué configuraciones incluiría

Uniendo lo que hoy ya existe (derivado, no como variable de entorno todavía) con lo que falta:

| Variable | Hoy | Con el loader |
|---|---|---|
| Ruta de la DB (`estadisticas.db`) | Calculada en `rutas.py`, fija | Podría permitir override (`STATSPRO_DB_PATH`) para testing o para que el usuario elija dónde guardar sus datos |
| Rutas de los `.sql` (schema/views/seed/limpieza) | Calculadas en `rutas.py` | Se quedan como están — son parte del código, no del entorno |
| Carpeta de logs | Calculada en `rutas.py` | Igual — parte del código |
| Nivel de logging | Fijo en `logger.py` (INFO al archivo) | `STATSPRO_LOG_LEVEL` — `DEBUG` en desarrollo, `INFO` o `WARNING` en producción, sin tocar código |
| Modo de base de datos | Implícito en cada test (`:memory:` a mano) | `STATSPRO_ENV=test` podría hacer que `Settings` fuerce `:memory:` automáticamente |
| Configuración de Ges Deportivo (Hito 2+) | No existe todavía | Si el formato de columnas cambia entre clubes, podría parametrizarse acá en vez de hardcodear en el parser |

La regla general: **si dos personas del equipo, o dos entornos (tu máquina / CI / la compu del
usuario final), necesitarían un valor distinto para lo mismo, es candidato a variable de
entorno.** Si el valor es siempre el mismo sin importar dónde corra (como las rutas relativas al
código), se queda en `rutas.py` tal cual está.

### Por qué separar esto de `rutas.py`

`rutas.py` responde "¿dónde, dentro de la carpeta del proyecto, está tal archivo?" — es
determinístico, no cambia según quién lo ejecute. Un loader de configuración responde "¿qué
comportamiento quiero en este entorno particular?" — sí cambia según quién y dónde lo ejecute. Son
preguntas distintas, aunque hoy convivan mezcladas en el mismo módulo por simplicidad (razonable
para el tamaño actual del proyecto).

### Cómo se conecta con el empaquetado final (Hito 4, US-404)

Esta es la parte más interesante a largo plazo. Cuando el proyecto pase de "lo corro con
`python src/main.py` desde mi entorno de desarrollo" a "lo distribuyo como un ejecutable que
alguien más instala en su computadora" (PyInstaller o `flet build`), **ya no existe un `.env` de
desarrollador** — el usuario final ni sabe qué es eso, y no tiene sentido pedirle que edite un
archivo de texto con sintaxis de variables de entorno.

En ese escenario, la configuración pasa a vivir en un archivo tipo
`~/.statspro/config.json` (o `%APPDATA%\StatsPro\config.json` en Windows) — un archivo que:

1. **Se genera automáticamente la primera vez que corre la app**, con valores por defecto
   sensatos (nivel de log INFO, ruta de DB en una carpeta estándar del usuario).
2. El usuario puede editarlo a mano si quiere cambiar algo (o, más adelante, la propia GUI en
   Flet podría tener una pantalla de "Configuración" que lo edite por él).

La pieza clave del diseño: **el mismo módulo `Settings` que en desarrollo lee del `.env` puede,
en el build empaquetado, leer de ese `config.json` en su lugar** — el resto de la aplicación
(los casos de uso, los repositorios, la UI) le siguen pidiendo valores a `Settings` exactamente
igual, sin enterarse de si la fuente real es un `.env`, variables de entorno del sistema, o un
JSON en el home del usuario. Es el mismo principio de **"Configuración Externalizada"** que
mencionamos charlando de otro proyecto (ahí aplicado a Kubernetes con ConfigMaps) — acá el
"entorno de despliegue" no es un clúster, es la computadora del entrenador que instaló la app,
pero el problema que resuelve es idéntico: que el comportamiento de la app dependa de dónde
corre, sin tener que tocar código para cada instalación.

## 5. Validadores de reglas de negocio como funciones puras

**Qué es:** en vez de meter toda la validación dentro de `__post_init__` de cada entidad, separar
funciones chicas y testeables (`validar_dni(dni: int) -> bool`,
`validar_fechas_afiliacion(desde: str, hasta: str | None) -> bool`) que las entidades usan
internamente.

**Por qué es un buen ejercicio:** funciones puras (mismo input → mismo output, sin efectos
secundarios) son lo más fácil de testear que existe en programación — ideal para practicar
`pytest` con casos borde antes de meterse con la lógica más compleja de la US-103.

**Dónde encajaría:** un módulo nuevo, por ejemplo `dominio/validaciones.py`, usado desde
`__post_init__` de las entidades que lo necesiten.

## 6. Un comando CLI mínimo, antes de construir toda la US-106

**Qué es:** antes de armar toda la infraestructura de Command Pattern que pide la US-106, un
experimento chico: un único archivo con `argparse` que soporte `stats club list` y lea
directamente de `v_partidos_resumen` (sin pasar por casos de uso todavía).

**Por qué es un buen ejercicio:** `argparse` tiene una curva de aprendizaje propia (subparsers,
argumentos posicionales vs. opcionales) — vale la pena practicarlo aislado, en un script chico
descartable, antes de comprometerse con la arquitectura completa de comandos que pide el PRD.

## 7. Completar el pipeline de CI (hoy solo lintea y testea)

Hoy `.github/workflows/` tiene dos jobs reales: `linter.yml` (ruff, solo reglas `E`/`I`) y
`test.yml` (pytest + cobertura, en Linux y Windows, sube el log como artifact si falla). Es una
base sólida, pero para que sea "un CI completo" en el sentido de lo que hace un equipo profesional
faltan piezas — cada una es chica de agregar (son pasos de YAML, no lógica nueva) y enseña un
concepto de CI/DevOps distinto:

### 7.1 Que la cobertura realmente bloquee el PR

`test.yml` genera el reporte de cobertura (`--cov-report=html`), pero **nada falla si la
cobertura es baja** — el PRD (US-108, AC1) pide explícitamente que el pipeline "falle si
cobertura < 80% en módulos no críticos", y hoy eso no está pasando. La forma más simple: agregar
`--cov-fail-under=80` al comando de `pytest` (o configurarlo directamente en `pytest.ini`, que ya
existe, con `[coverage:report] fail_under = 80`). Es literalmente un flag — el ejercicio de
aprendizaje acá es entender la diferencia entre "medir" algo y "hacer que ese número tenga
consecuencias".

### 7.2 Chequeo de formato, no solo de lint

`ruff check --select E --select I` valida estilo (E) e imports ordenados (I), pero **no valida
que el código esté formateado** de manera consistente — eso es un chequeo distinto
(`ruff format --check .`, que falla si algún archivo no está formateado como lo formatearía
`ruff format`, sin modificarlo). Ya tienen `black` en `.pre-commit-config.yaml` para el hook
local; vale la pena decidir (con un ADR chico, si quieren) si el formateador oficial del proyecto
es `black` o `ruff format`, y que el CI valide exactamente eso — hoy el CI no valida ningún
formateador, solo estilo/imports.

### 7.3 Revisión de tipos con `mypy`

El código ya usa type hints en todos lados (`int | None`, `list[Club]`, etc.), pero nada verifica
que esos tipos sean consistentes — `mypy` (o `pyright`) los analiza estáticamente y detecta, por
ejemplo, que una función declarada `-> Club` en realidad puede devolver `None` (que es
justo lo que pasa hoy en `sqlite_club_repositorio.py::buscar_por_id`, que devuelve `None` pero
está tipado como `-> Club`, no `-> Club | None`). Es un buen ejercicio para aprender qué tan en
serio se puede tomar Python con tipado gradual, y probablemente va a encontrar un par de
inconsistencias reales como esa en el código actual.

### 7.4 Escaneo de dependencias con vulnerabilidades conocidas

Un paso con `pip-audit` (herramienta oficial del packaging de Python) que revisa
`requerimientos.txt` contra una base de datos de vulnerabilidades conocidas (CVEs) y falla el
build si alguna dependencia instalada tiene una vulnerabilidad reportada. Es un paso de una sola
línea (`pip install pip-audit && pip-audit -r requerimientos.txt`) y es exactamente el tipo de
chequeo que un proyecto "profesional" tiene y uno de aprendizaje normalmente no — buena
introducción al concepto de *supply chain security* sin ninguna complejidad de implementación.

### 7.5 Detección de secretos accidentales

Un paso (ej. con la acción `gitleaks`) que escanea el diff del PR buscando patrones de
contraseñas, tokens o claves que se hayan subido por error. Particularmente relevante acá porque
el proyecto maneja hashes de contraseñas y, más adelante, quizás credenciales de la base de datos
o de algún servicio externo (Ges Deportivo). Es un solo paso de YAML, sin configuración adicional
para el caso base.

### 7.6 Validar que el schema/vistas SQL siguen siendo válidos, aislado de pytest

Ya está cubierto indirectamente por `test.yml` (que corre toda la suite, incluidos
`test_schema_sql_ejecuta_sin_errores` y `test_views_sql_ejecuta_sin_errores`), así que esto no es
un job nuevo — es más una nota: si el proyecto crece y separar "tests rápidos" de "tests de
integración con DB" empieza a tener sentido (con markers de pytest, `@pytest.mark.integration`),
ahí sí valdría la pena un job de CI aparte que corra primero los rápidos y falle temprano antes
de gastar tiempo en los de integración. Por ahora, con 19 tests que corren en menos de un
segundo, no hace falta — mencionarlo para cuando la suite crezca.

### 7.7 Actualización automática de dependencias

Un archivo `.github/dependabot.yml` (nada de workflow, es configuración declarativa que lee
GitHub directamente) que abre un PR automático cada vez que una dependencia de
`requerimientos.txt` tiene una versión nueva. Cero mantenimiento una vez configurado, y es la
forma más simple de no terminar con dependencias congeladas en versiones de hace un año.

### 7.8 Build de la imagen Docker, si llegan a armarla

Si terminan armando el `Dockerfile` de `docs/guias/docker-para-tests.md`, un paso lindo para
sumar después es que el propio CI construya la imagen en cada PR (`docker build .`) — así un
`Dockerfile` roto se detecta en el PR, no cuando alguien lo necesita usar. Directamente conecta
esta idea con la guía de Docker que ya armamos.

**Para no perderse en la lista:** si tuvieran que elegir con qué arrancar, el orden de
"impacto vs. esfuerzo" sería 7.1 (cobertura real) → 7.3 (mypy, porque ya encontró un bug real de
tipado arriba) → 7.4/7.5 (seguridad, un paso cada uno) → el resto según les vaya interesando.
