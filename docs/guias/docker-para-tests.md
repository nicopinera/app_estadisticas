# Guía: Docker para correr los tests (ejercicio de aprendizaje)

> Esta guía explica los conceptos y qué archivos harían falta. **No incluye el Dockerfile
> terminado** — la idea es que lo escriban ustedes como ejercicio, usando esto como mapa.

## El problema que resuelve

Hoy, para correr `make run_test` alguien necesita: Python instalado (¿qué versión exacta?),
`pip install -r requerimientos.txt`, y que su sistema operativo no tenga ninguna diferencia rara
con el de otro miembro del equipo. "En mi máquina funciona" es el síntoma clásico de no tener
esto resuelto.

**Docker** empaqueta "el proyecto + todo lo que necesita para correr" en una **imagen** —un
molde inmutable— que después se ejecuta como **contenedor** en cualquier máquina que tenga Docker
instalado, sin importar qué versión de Python tenga esa máquina por fuera. Es la misma idea que
ya vimos conceptualmente en otro proyecto (EOP): "empaquetar las dependencias exactas una vez, y
correr siempre igual en cualquier lado".

## Los dos archivos que harían falta

### 1. `Dockerfile`

Define, paso a paso, cómo se construye la imagen. Para este proyecto, a alto nivel, tendría:

1. **Imagen base:** algo como `python:3.13-slim` — ya trae Python instalado, sin todo el peso de
   una distribución Linux completa (por eso `slim`).
2. **Directorio de trabajo:** un `WORKDIR /app` para que todo lo que se copie después caiga en un
   lugar predecible dentro del contenedor.
3. **Copiar solo lo necesario para instalar dependencias primero:** copiar `requerimientos.txt`
   y correr `pip install -r requerimientos.txt` **antes** de copiar el resto del código. Esto no
   es capricho — Docker cachea cada paso (cada instrucción del Dockerfile es una "capa"); si
   copiás el código fuente antes de instalar dependencias, cualquier cambio en un archivo `.py`
   invalida el cache de la instalación de dependencias y hay que reinstalar todo de nuevo cada
   vez. Copiando `requerimientos.txt` primero, mientras no cambien las dependencias, ese paso se
   reusa cacheado y el build es mucho más rápido.
4. **Copiar el resto del proyecto:** `src/`, `test/`, `pytest.ini`, `pyproject.toml`.
5. **Comando por defecto:** algo como `CMD ["pytest", "-v", "--cov=src", "--cov-report=term"]` —
   así, al correr el contenedor sin argumentos extra, automáticamente corre la suite de tests.

### 2. `.dockerignore`

Igual que un `.gitignore`, pero para decirle a Docker qué **no** copiar dentro de la imagen —
evita meter basura (entorno virtual local, `__pycache__`, `.pytest_cache`, `.git`, el propio
`estadisticas.db` de desarrollo) que infla la imagen sin necesidad y puede filtrar datos locales
que no deberían viajar en la imagen.

## Cómo se usaría, una vez armado

```bash
docker build -t app-estadisticas-tests .
docker run --rm app-estadisticas-tests
```

`docker build` lee el `Dockerfile` y arma la imagen (una sola vez, o cada vez que cambia algo).
`docker run --rm` levanta un contenedor a partir de esa imagen, corre el comando por defecto
(los tests), y `--rm` lo borra automáticamente al terminar (no queda un contenedor muerto
acumulándose en el disco).

## Qué probar para saber que quedó bien armado

- [ ] `docker build` termina sin errores y sin necesitar tocar nada del `Dockerfile` a mano
      después.
- [ ] `docker run --rm app-estadisticas-tests` corre los **mismos 19 tests** que corren hoy con
      `make run_test` fuera de Docker, con el mismo resultado (todos en verde).
- [ ] Si borrás tu entorno virtual local y corrés *solo* el contenedor, igual funciona — esa es
      la prueba real de que la imagen no depende de nada de tu máquina por fuera de Docker mismo.
- [ ] El tamaño de la imagen final (`docker images`) es razonable — si ronda varios GB, algo del
      `.dockerignore` probablemente no está filtrando bien.

## Una idea para más adelante (no ahora)

Cuando el proyecto tenga `docker-compose.yml` con más de un servicio (por ejemplo, si en el
Hito 3/4 suman algo como una base de datos aparte para pruebas, o el perfil de observabilidad que
ya está mencionado en el PRD para Seq), un segundo contenedor liviano solo para tests es un buen
lugar para aprender la diferencia entre una imagen de **desarrollo** (con todas las herramientas:
`ruff`, `pytest-cov`, etc.) y una de **producción** (solo lo mínimo para que la app corra) — el
mismo concepto de *multi-stage build* que ya vimos en el proyecto EOP, aplicable acá el día que
quieran optimizar el tamaño de la imagen final para distribución (Hito 4, empaquetado).
