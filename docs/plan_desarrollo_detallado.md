# Plan de Desarrollo: StatsPro Basketball

> **Qué es este documento:** la referencia de trabajo del día a día del equipo — versión
> simplificada del PRD formal. El documento "oficial" (con perfiles de usuario relevados,
> ADRs y el detalle exhaustivo AC por AC) vive en el submódulo
> `docs/documentacion_app_estadistica/PRD/Plan_Requerimientos_Producto_Pro.tex` (y su PDF). Si
> hay una duda de alcance/negocio, ese es el documento que manda; este archivo es el resumen
> operativo para no tener que abrir el PDF cada vez que arrancamos una historia de usuario.
>
> **Última actualización:** sincronizado contra la versión más reciente del submódulo (esta copia
> estaba desactualizada — le faltaba el repositorio de competencia en varias secciones).

---

## 1. Qué es el proyecto

Aplicación de escritorio (Python + SQLite, 100% offline) para que entrenadores de básquet
formativo carguen partidos y obtengan estadísticas avanzadas (eFG%, EFF, PPP, tendencias),
sin depender de conexión a internet ni de cálculos manuales. Diferencial clave: importación
automática de planillas Excel de "Ges Deportivo".

**No metas (v1.0):** carga de datos en vivo durante el partido, sincronización en la nube,
integración por API directa con Ges Deportivo. Se prioriza simplicidad y carga rápida
(objetivo: <20 min por partido) sobre funcionalidad exhaustiva.

**Stack:** Python · SQLite · Pandas · pytest/pytest-cov · ruff · Flet (candidato a UI, pendiente
de ADR-002).

## 2. Arquitectura, en una tabla

Ver `docs/arquitectura.md` para el detalle completo (capas, DI, patrones, ejemplos de código).
Resumen:

| Capa | Carpeta | Puede importar | Responsabilidad |
|---|---|---|---|
| Dominio | `src/dominio/` | nada externo | Entidades (`@dataclass`), interfaces de repositorio (`ABC`), excepciones |
| Aplicación | `src/aplicacion/` *(a crear)* | solo `dominio` | Casos de uso, DTOs, servicios (sesión, contexto) |
| Infraestructura | `src/infraestructura/` | `dominio` + libs externas | Repositorios SQLite, parser Excel, motor Pandas, UI, seguridad |

Patrones en uso: **Repository** (una interfaz por agregado + su implementación SQLite),
**Inyección de Dependencias** (los casos de uso reciben repositorios por constructor, nunca los
instancian), **Command Pattern** (para la futura CLI, un archivo = un grupo de subcomandos).

### Estructura de Repositorios (agregados de datos)

> **Corregido en esta actualización:** faltaba la fila de Competencia en esta tabla — está
> mencionada en el texto de la US-102 pero no había quedado reflejada acá.

| Agregado | Interfaz (dominio) | Implementación (infraestructura) | Tablas que maneja |
|---|---|---|---|
| Identidad | `UsuarioRepositorio` | `SqliteUsuarioRepositorio` | `usuario` |
| Clubes | `ClubRepositorio` | `SqliteClubRepositorio` | `club`, `usuarioClub` |
| Jugadores | `JugadorRepositorio` | `SqliteJugadorRepositorio` | `jugador`, `jugadorClub` |
| **Competencia** | `CompetenciaRepositorio` | `SqliteCompetenciaRepositorio` | `competencia`, `categoria`, `inscripcion`, `listaBuenaFe`, `jugadorListaBuenaFe` |
| Partidos/Stats | `JuegoRepositorio` | `SqliteJuegoRepositorio` | `partido`, `jugadorPartido` |

Se agrupan `competencia`/`categoria`/`inscripcion`/`listaBuenaFe`/`jugadorListaBuenaFe` en **un
solo repositorio** (no cinco) porque son un único agregado conceptual: una inscripción no existe
sin su competencia+categoría, y una lista de buena fe no existe sin su inscripción (relación 1:1).

## 3. Estado real del código vs. este plan (deuda técnica conocida)

Auditoría hecha releyendo `src/` completo contra este plan. Documentado acá para que quien
retome el código sepa exactamente por dónde empezar — **nada de esto se corrigió en esta
sesión, es solo el diagnóstico**:

- ❌ **Falta la implementación `SqliteCompetenciaRepositorio`.** La interfaz
  `dominio/repositorios/competencia_repositorio.py` ya existe completa (12 métodos abstractos);
  no tiene ninguna clase concreta en `infraestructura/repositorios/` todavía. Es el próximo paso
  natural de la US-102.
- ❌ **Las 4 implementaciones SQLite que sí existen** (`sqlite_club_repositorio.py`,
  `sqlite_juego_repositorio.py`, `sqlite_jugador_repositorio.py`,
  `sqlite_usuario_repositorio.py`) **importan una clase que no existe en el proyecto**:
  `from infraestructura.persistencia.sqlite_conexion import SqliteConexion`. Ese archivo nunca se
  creó. Como consecuencia, **ninguno de los 4 repositorios se puede importar hoy** (fallaría con
  `ModuleNotFoundError` en cuanto algo intente usarlos). Esto no se detectó antes porque los 19
  tests actuales (`test/`) solo ejercitan `database_manager.py` y el SQL crudo — ninguno importa
  todavía los repositorios de `infraestructura/repositorios/`. Antes de escribir el repositorio de
  competencia hace falta resolver esta pieza faltante (una clase `SqliteConexion` que envuelva al
  `SQLiteManager` y exponga `obtener_conexion()`, que es lo que los 4 repos ya esperan).
- ❌ **`sqlite_juego_repositorio.py` y `sqlite_usuario_repositorio.py` apuntan a tablas/columnas
  que no coinciden con `schema.sql`:**
  - `sqlite_juego_repositorio.py` usa la tabla `Juego` (no existe; la tabla real es `partido`) y
    la columna `idJuego` (real: `idPartido`). El `INSERT` de `guardar_boxscore` además tiene la
    lista de columnas desalineada de la lista de valores (le falta `idClub` en la lista de
    columnas, pero sí está en los valores — un `INSERT` así falla en tiempo de ejecución).
  - `sqlite_usuario_repositorio.py` usa la tabla `Usuarios` (real: `usuario`, singular/minúscula)
    y la columna `id_usuario` (real: `idUsuario`). También asume una columna `pw` en la tabla
    (la columna real en `schema.sql` es `contrasenia`) — la entidad de dominio `Usuario` sí puede
    seguir llamándose `pw` en Python, pero el repositorio tiene que mapear ese campo a la columna
    `contrasenia` en el SQL, no asumir que se llaman igual.
- ⚠️ **Las entidades de dominio son `@dataclass` simples**, sin las validaciones que esta US
  pide (`__post_init__`, `calcular_edad()`, DNI/fechas). Es esperable — la US-103 (que agrega esa
  lógica) todavía no se implementó, no es un bug.
- ✅ **`SQLiteManager` (`database_manager.py`) está sólido:** conexión, `PRAGMA foreign_keys`,
  `row_factory`, inicialización de schema/vistas/seed/limpieza, todo con manejo de errores y
  logueado. Tiene 15 tests de integración reales cubriendo constraints, FKs, vistas y división por
  cero. Es la base más madura del proyecto hoy — el resto se apoya en ella.

## 4. Hitos, en formato compacto

> Para el detalle exhaustivo AC-por-AC de cada historia (útil cuando ya estás implementando una
> US puntual), abrí el PRD del submódulo. Acá solo el resumen para planificar.

### Hito 1 — Núcleo de Datos e Interfaz CLI (v0.1)

**Objetivo:** persistencia robusta + gestión básica de entidades por consola.

| Épica | US | Qué hace | AC principales |
|---|---|---|---|
| E1 · Infra y Persistencia | US-101 | Schema SQLite + 4 vistas + seed | Schema idempotente con `CHECK`s; vistas sin división por cero; seed poblado |
| | US-102 | `DatabaseManager` + Repository Pattern (5 agregados, ver tabla arriba) | Dominio no importa `sqlite3`/`pandas`; repos devuelven dataclasses, no tuplas; `save_boxscore` transaccional |
| E2 · Lógica y CLI | US-103 | Casos de uso admin (jugadores, clubes, competencias, inscripciones) | Validación fail-fast (DNI, fechas); DI por constructor; operaciones de inscripción atómicas |
| | US-104 | Auth + sesión local (club activo persistente) | Passwords nunca en texto plano; sesión sobrevive reinicios de CLI |
| | US-105 | Carga atómica de partido + boxscore | Rollback total ante fallo parcial; validación antes de tocar la DB |
| | US-106 | CLI con Command Pattern | Nuevo grupo de comandos = 1 archivo nuevo, sin tocar el resto |
| | US-107 | Logging estructurado + `correlation_id` | JSON estructurado; secretos redactados; mismo `correlation_id` en todo un comando |
| E3 · Calidad y CI/CD | US-108 | Pipeline CI (lint + test + cobertura) | `make test`/`make lint` fallan el PR si no cumplen umbral |

### Hito 2 — Motor de Ingesta y Análisis (v0.2)

**Objetivo:** automatizar carga desde Excel (Ges Deportivo) + métricas avanzadas con Pandas.
**Bloqueante previo:** ADR-003 (protocolo de ingesta).

| Épica | US | Qué hace | AC principales |
|---|---|---|---|
| E1 · Ingesta Ges Deportivo | US-201 | Parser Excel + merge por DNI | Modo `preview` sin persistir; atómico por partido; reporte de creados/rechazados |
| E2 · Motor Estadístico | US-202 | Fórmulas puras (eFG%, EFF, PPP, posesiones, %rebotes) | `formulas.py` sin acceso a DB; división por cero → 0.0, nunca NaN |
| E3 · Inteligencia (Pandas) | US-203 | Conecta vistas SQL con las fórmulas | `AnalyticsService` solo lee de vistas; columnas estandarizadas |
| | US-205 | Consulta estadística por CLI (`stats show/leaders/compare`) | Salida tabular; filtros por temporada/competencia |
| E3 · Gobernanza de Esquema | US-204 | Versionado de DB + migraciones | Tabla `schema_version`; runner idempotente; rollback de la última migración |

### Hito 3 — Visualización Pro y Reporting (v0.3)

**Objetivo:** dashboards en consola + exportación PDF + scouting de rival.
**Bloqueante previo:** ADR-005 (librería PDF), ADR-007 (librería de gráficos).

| Épica | US | Qué hace | AC principales |
|---|---|---|---|
| E1 · Dashboards | US-301 | Top-5 líderes + gráficos de tendencia | Gráfico en <2s; valores consistentes con las vistas SQL |
| E2 · Reportería | US-302 | Exportación a PDF | Nombre de archivo con convención fija; carpeta `exports/` autocreada |
| E3 · Scouting | US-303 | Reporte táctico pre-partido del rival | Ventana de últimos N partidos configurable; detección de rachas |

### Hito 4 — Interfaz Multiplataforma y Entrega (v1.0)

**Objetivo:** UI visual completa (Flet), hardening de seguridad, backup/restore, empaquetado.
**Bloqueante previo:** ADR-002 (Flet confirmado).

| Épica | US | Qué hace | AC principales |
|---|---|---|---|
| E1 · GUI | US-401 | Pantallas Flet (Dashboard, GameEntry, PlayerProfile, Import) | Arranque <3s; tema claro/oscuro; UI sin lógica de negocio propia |
| E2 · Resiliencia | US-402 | Backup/restore de la DB | Verificación de integridad post-restore |
| E3 · Seguridad | US-403 | Hardening (passwords, cifrado opcional, política de sesión) | Contraseñas ≥12 caracteres; hash robusto (bcrypt/Argon2) |
| E4 · Empaquetado | US-404 | Binarios autónomos (PyInstaller/Flet build) | Ejecutable sin requerir Python instalado en la máquina del usuario |

## 5. ADRs pendientes

Ninguno está escrito todavía (solo existe la plantilla en
`docs/documentacion_app_estadistica/ADR/template_adr.md`). Bloquean el hito indicado:

| ADR | Decisión a tomar | Bloquea |
|---|---|---|
| ADR-001 | Arquitectura local-first | ✅ ya resuelto (SQLite + offline) |
| ADR-002 | Framework de UI (Flet vs. Compose Multiplatform) | Hito 4 |
| ADR-003 | Protocolo de ingesta Excel (mapeo de columnas Ges Deportivo) | US-201 |
| ADR-004 | Versionado de DB (migraciones manuales vs. Alembic) | Hito 2 |
| ADR-005 | Librería de reportes PDF (ReportLab vs. WeasyPrint) | US-302 |
| ADR-006 | Seguridad/cifrado (hash de passwords, SQLCipher) | US-106 / Hito 4 |
| ADR-007 | Motor de visualización (matplotlib vs. plotly) | US-301 |
| ADR-008 | Estrategia de backup | Hito 4 |
| ADR-009 | Pipeline CI/CD | US-108 |

## 6. Convenciones rápidas

- **Commits:** `tipo: descripción corta` (`FEAT`, `FIX`, `DOCS`, `STYLE`, `REFACTOR`, `PERF`,
  `TEST`) — ver `docs/info_modulo/02-reglas.md`.
- **Interfaces de repositorio:** el proyecto terminó usando `ABC`/`@abstractmethod` (no
  `typing.Protocol`, que es lo que sugiere `docs/info_protocolos.md`). Ambas son válidas; vale la
  pena un ADR corto si se quiere dejar asentado por qué se eligió `ABC` en la práctica.
- **Logging:** `infraestructura/logger.py` ya está armado (rotación 10MB, 5 backups, nivel INFO+
  a archivo). Ver `docs/info_modulo/01-logger.md` para el detalle conceptual de qué es un logger y
  por qué se usa en vez de `print()`.
