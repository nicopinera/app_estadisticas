# Plan de Desarrollo Detallado v2: StatsPro Basketball

> **Propósito de este documento:** Especificación técnica completa por Historia de Usuario.
> Cada US debe ser autosuficiente: al leerla, el desarrollador sabe qué archivos crear,
> qué clases implementar, qué lógica de negocio aplicar y qué tests escribir.

---

## Convenciones del Documento

### Tipos de Artefactos de Código

| Símbolo      | Tipo Python          | Cuándo usarlo                                                        |
| ------------ | -------------------- | -------------------------------------------------------------------- |
| `@dataclass` | Dataclass            | Entidades de dominio y DTOs (datos sin comportamiento complejo)      |
| `Protocol`   | Interface/Puerto     | Contratos de repositorios en la capa `domain/interfaces/`            |
| `class`      | Clase concreta       | Implementaciones en `infrastructure/` y `application/`               |
| `UseCase`    | Clase de caso de uso | Orquestadores en `application/use_cases/`                            |
| `ABC`        | Clase abstracta      | Solo si se necesita comportamiento compartido entre implementaciones |

### Estructura de Directorios de Referencia

```text
src/
├── main.py
├── domain/
│   ├── entities/           # @dataclass puras, sin imports externos
│   ├── interfaces/         # Protocol de repositorios
│   ├── exceptions.py       # Excepciones de negocio
│   └── services/           # Lógica de dominio compleja (opcional)
├── application/
│   ├── use_cases/          # Orquestadores (reciben repos por DI)
│   ├── dtos/               # Dataclasses de entrada/salida entre capas
│   └── services/           # Servicios de aplicación (ej: SessionManager)
├── infrastructure/
│   ├── persistence/
│   │   ├── sql/            # schema.sql, views.sql, seed.sql
│   │   ├── database_manager.py
│   │   └── sqlite_*_repository.py
│   ├── analytics/          # Motor Pandas
│   ├── ingest/             # Parser Excel
│   ├── reports/            # Generador PDF
│   ├── security/           # PasswordHasher
│   └── ui/
│       ├── cli/            # Interfaz de línea de comandos
│       └── flet/           # GUI (Hito 2+)
└── tests/
    ├── unit/               # Sin DB, con mocks
    ├── integration/        # Con DB en memoria (:memory:)
    └── conftest.py         # Fixtures compartidos (db_in_memory, seeded_db)
```

### Regla de Dependencias (Clean Architecture)

```text
domain  ←  application  ←  infrastructure
  ↑                               ↑
  └─────── NO puede importar ─────┘
```

`domain/` no puede importar nada de `application/` ni de `infrastructure/`.
`application/` puede importar de `domain/`, pero NO de `infrastructure/`.

---

---

## HITO 1: Núcleo de Datos e Interfaz CLI (v0.1)

**Objetivo:** Sistema funcional por línea de comandos con persistencia robusta.

---

### Épica E1: Infraestructura y Persistencia

---

#### US-101: Schema SQL, Vistas y Datos Semilla

**Narrativa:** Como desarrollador, quiero el esquema relacional completo en SQLite, con sus vistas de análisis y datos de prueba, para tener una base verificable sobre la que construir el sistema.

**Dependencias previas:** Ninguna. Es el punto de partida.

---

**Archivos a crear:**

```text
src/infrastructure/persistence/sql/
├── schema.sql      ← Definición de todas las tablas (DDL)
├── views.sql       ← Definición de las 4 vistas de análisis
└── seed.sql        ← Datos de prueba completos para desarrollo

tests/
└── test_database_schema.py
```

---

**Tablas a implementar** (basado en el Diccionario de Datos `inicioDDD.pdf`):

```sql
-- Orden de creación respetando dependencias FK

CREATE TABLE IF NOT EXISTS usuario (
    idUsuario   INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT    NOT NULL,
    email       TEXT    NOT NULL UNIQUE,
    contrasena  TEXT    NOT NULL          -- siempre almacenar hash, nunca texto plano
);

CREATE TABLE IF NOT EXISTS club (
    idClub  INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre  TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS usuarioClub (
    idUsuario       INTEGER NOT NULL,
    idClub          INTEGER NOT NULL,
    rolEntrenador   TEXT    NULL,
    PRIMARY KEY (idUsuario, idClub),
    FOREIGN KEY (idUsuario) REFERENCES usuario(idUsuario) ON DELETE CASCADE,
    FOREIGN KEY (idClub)    REFERENCES club(idClub)       ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS categoria (
    idCategoria INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS competencia (
    idCompetencia   INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre          TEXT    NOT NULL,
    anio            INTEGER NOT NULL CHECK(anio > 1900),
    tipo            TEXT    NULL
);

CREATE TABLE IF NOT EXISTS inscripcion (
    idInscripcion   INTEGER PRIMARY KEY AUTOINCREMENT,
    idClub          INTEGER NOT NULL,
    idCategoria     INTEGER NOT NULL,
    idCompetencia   INTEGER NOT NULL,
    FOREIGN KEY (idClub)        REFERENCES club(idClub)              ON DELETE CASCADE,
    FOREIGN KEY (idCategoria)   REFERENCES categoria(idCategoria),
    FOREIGN KEY (idCompetencia) REFERENCES competencia(idCompetencia) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS jugador (
    idJugador       INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre          TEXT    NOT NULL,
    apellido        TEXT    NOT NULL,
    dni             TEXT    NULL UNIQUE,    -- NULL si no se conoce; UNIQUE para evitar duplicados
    anioNacimiento  INTEGER NULL
);

CREATE TABLE IF NOT EXISTS jugadorClub (
    idJugador   INTEGER NOT NULL,
    idClub      INTEGER NOT NULL,
    fechaDesde  TEXT    NOT NULL,   -- formato ISO: YYYY-MM-DD
    fechaHasta  TEXT    NULL,       -- NULL = vínculo activo actualmente
    PRIMARY KEY (idJugador, idClub, fechaDesde),
    FOREIGN KEY (idJugador) REFERENCES jugador(idJugador) ON DELETE CASCADE,
    FOREIGN KEY (idClub)    REFERENCES club(idClub)       ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS listaBuenaFe (
    idListaBuenaFe      INTEGER PRIMARY KEY AUTOINCREMENT,
    fechaPresentacion   TEXT    NULL,
    idInscripcion       INTEGER NOT NULL UNIQUE,    -- UNIQUE refuerza la relación 1:1
    FOREIGN KEY (idInscripcion) REFERENCES inscripcion(idInscripcion) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS jugadorListaBuenaFe (
    idJugador       INTEGER NOT NULL,
    idListaBuenaFe  INTEGER NOT NULL,
    PRIMARY KEY (idJugador, idListaBuenaFe),
    FOREIGN KEY (idJugador)      REFERENCES jugador(idJugador)            ON DELETE CASCADE,
    FOREIGN KEY (idListaBuenaFe) REFERENCES listaBuenaFe(idListaBuenaFe)  ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS partido (
    idPartido       INTEGER PRIMARY KEY AUTOINCREMENT,
    idCompetencia   INTEGER NOT NULL,
    fecha           TEXT    NOT NULL,   -- formato ISO: YYYY-MM-DD HH:MM
    estadio         TEXT    NULL,
    idClubLocal     INTEGER NOT NULL,
    idClubVisitante INTEGER NOT NULL,
    CHECK (idClubLocal != idClubVisitante),
    FOREIGN KEY (idCompetencia)  REFERENCES competencia(idCompetencia),
    FOREIGN KEY (idClubLocal)    REFERENCES club(idClub),
    FOREIGN KEY (idClubVisitante) REFERENCES club(idClub)
);

CREATE TABLE IF NOT EXISTS jugadorPartido (
    idJugador           INTEGER NOT NULL,
    idPartido           INTEGER NOT NULL,
    idClub              INTEGER NOT NULL,
    minutosJugados      INTEGER NOT NULL DEFAULT 0 CHECK(minutosJugados >= 0),
    puntos              INTEGER NOT NULL DEFAULT 0 CHECK(puntos >= 0),
    T2C                 INTEGER NOT NULL DEFAULT 0 CHECK(T2C >= 0),
    T2L                 INTEGER NOT NULL DEFAULT 0 CHECK(T2L >= 0),
    T3C                 INTEGER NOT NULL DEFAULT 0 CHECK(T3C >= 0),
    T3L                 INTEGER NOT NULL DEFAULT 0 CHECK(T3L >= 0),
    T1C                 INTEGER NOT NULL DEFAULT 0 CHECK(T1C >= 0),
    T1L                 INTEGER NOT NULL DEFAULT 0 CHECK(T1L >= 0),
    rebotesDefensivos   INTEGER NOT NULL DEFAULT 0 CHECK(rebotesDefensivos >= 0),
    rebotesOfensivos    INTEGER NOT NULL DEFAULT 0 CHECK(rebotesOfensivos >= 0),
    asistencias         INTEGER NOT NULL DEFAULT 0 CHECK(asistencias >= 0),
    recuperos           INTEGER NOT NULL DEFAULT 0 CHECK(recuperos >= 0),
    perdidas            INTEGER NOT NULL DEFAULT 0 CHECK(perdidas >= 0),
    taponesRecibidos    INTEGER NOT NULL DEFAULT 0 CHECK(taponesRecibidos >= 0),
    taponesRealizados   INTEGER NOT NULL DEFAULT 0 CHECK(taponesRealizados >= 0),
    faltasRecibidas     INTEGER NOT NULL DEFAULT 0 CHECK(faltasRecibidas >= 0),
    faltasCometidas     INTEGER NOT NULL DEFAULT 0 CHECK(faltasCometidas >= 0),
    -- Regla de consistencia: convertidos no puede superar lanzados
    CHECK(T2C <= T2L),
    CHECK(T3C <= T3L),
    CHECK(T1C <= T1L),
    PRIMARY KEY (idJugador, idPartido),
    FOREIGN KEY (idJugador) REFERENCES jugador(idJugador),
    FOREIGN KEY (idPartido) REFERENCES partido(idPartido) ON DELETE CASCADE,
    FOREIGN KEY (idClub)    REFERENCES club(idClub)
);
```

---

**Vistas a implementar en `views.sql`** (del archivo `vistas_sql.md`):

Las 4 vistas deben crearse con `CREATE VIEW IF NOT EXISTS`:

1. `v_partidos_resumen` — Para listados en UI, reemplaza IDs por nombres.
2. `v_boxscore_completo` — Fuente principal para análisis por partido en Pandas.
3. `v_jugador_totales_temporada` — Acumulados históricos por jugador y año.
4. `v_listas_detalle` — Jugadores habilitados por inscripción.

> Ver el código completo de cada vista en el archivo `vistas_sql.md`.
> **Nota técnica:** En `v_jugador_totales_temporada`, toda división debe protegerse:
> `CASE WHEN SUM(T3L) > 0 THEN ROUND(CAST(SUM(T3C) AS FLOAT) / SUM(T3L) * 100, 2) ELSE 0.0 END`

---

**Datos Semilla (`seed.sql`) — escenario mínimo verificable:**

| Entidad             | Cantidad | Detalle                                           |
| ------------------- | -------- | ------------------------------------------------- |
| usuario             | 1        | email: `test@stats.com`, password: hash de "1234" |
| club                | 2        | "Club Atletico Norte", "Club Deportivo Sur"       |
| categoria           | 1        | "U17"                                             |
| competencia         | 1        | "Liga Provincial 2025", anio: 2025, tipo: "Liga"  |
| inscripcion         | 2        | Una por club en la misma competencia/categoría    |
| listaBuenaFe        | 2        | Una por inscripción                               |
| jugador             | 10       | 5 por club, con DNI numérico único                |
| jugadorClub         | 10       | Vínculo activo para cada jugador en su club       |
| jugadorListaBuenaFe | 10       | 5 jugadores por lista                             |
| partido             | 2        | Partido 1: Norte vs Sur. Partido 2: Sur vs Norte  |
| jugadorPartido      | ~20      | Stats variadas para 5 jugadores por partido       |

---

**Criterios de Aceptación:**

**AC1 — Schema robusto:**

- Todas las tablas usan `CREATE TABLE IF NOT EXISTS` (idempotencia).
- Existe un bloque `DROP TABLE IF EXISTS` antes de cada `CREATE TABLE` en el script, en orden inverso de dependencias, para facilitar el desarrollo (`DROP TABLE IF EXISTS jugadorPartido; DROP TABLE IF EXISTS partido; ...`).
- El `CHECK(idClubLocal != idClubVisitante)` en `partido` es verificable.
- El `UNIQUE` en `listaBuenaFe.idInscripcion` refuerza la relación 1:1.
- El campo `dni` en `jugador` es `UNIQUE` pero permite `NULL` (múltiples jugadores pueden no tener DNI cargado sin violar la restricción).

**AC2 — Vistas implementadas:**

- Las 4 vistas del catálogo existen en `views.sql` y son consultables tras ejecutar el schema.
- `v_boxscore_completo` incluye la columna `idClub` para permitir filtrar por equipo desde Pandas.
- Las divisiones en las vistas nunca producen errores por división por cero (usar `CASE WHEN ... > 0 THEN ... ELSE 0.0 END`).

**AC3 — Datos Semilla:**

- `seed.sql` se ejecuta limpiamente sobre un schema vacío sin errores de FK.
- Las estadísticas de los 2 partidos tienen valores variados (no todos ceros) para que las vistas devuelvan datos significativos.

**Tests a escribir en `tests/test_database_schema.py`:**

```python
# Fixture compartido (agregar a tests/conftest.py):
# db_in_memory → crea SQLite :memory:, ejecuta schema.sql + views.sql

def test_all_12_tables_exist(db_in_memory): ...
# Verifica: usuario, club, usuarioClub, categoria, competencia,
#           inscripcion, jugador, jugadorClub, listaBuenaFe,
#           jugadorListaBuenaFe, partido, jugadorPartido

def test_all_4_views_exist(db_in_memory): ...
# Verifica: v_partidos_resumen, v_boxscore_completo,
#           v_jugador_totales_temporada, v_listas_detalle

def test_fk_violation_on_partido_with_invalid_club(db_in_memory): ...
# INSERT INTO partido con idClubLocal inexistente debe lanzar IntegrityError

def test_check_constraint_rejects_negative_puntos(db_in_memory): ...
# INSERT INTO jugadorPartido con puntos = -1 debe lanzar IntegrityError

def test_check_constraint_rejects_t2c_greater_than_t2l(db_in_memory): ...
# INSERT INTO jugadorPartido con T2C=5, T2L=3 debe lanzar IntegrityError

def test_check_constraint_rejects_same_club_local_visitante(db_in_memory): ...
# INSERT INTO partido con idClubLocal = idClubVisitante debe lanzar IntegrityError

def test_seed_loads_without_errors(db_in_memory): ...
# Ejecutar seed.sql sobre schema limpio no lanza excepciones

def test_v_partidos_resumen_returns_names_not_ids(seeded_db): ...
# SELECT * FROM v_partidos_resumen → columna "club_local" contiene texto, no int

def test_v_jugador_totales_handles_zero_shots(seeded_db): ...
# Si hay jugador con T3L=0, la vista retorna 0.0, no NULL ni error
```

---

#### US-102: DatabaseManager y Patrón Repository

**Narrativa:** Como desarrollador, quiero una capa de infraestructura que gestione el ciclo de vida de la conexión SQLite y exponga repositorios tipados para cada agregado del dominio.

**Dependencias previas:** US-101.

---

**Archivos a crear:**

```text
src/infrastructure/persistence/
├── database_manager.py              ← clase SQLiteManager
├── sqlite_user_repository.py        ← implementa UserRepository
├── sqlite_club_repository.py        ← implementa ClubRepository
├── sqlite_player_repository.py      ← implementa PlayerRepository
└── sqlite_game_repository.py        ← implementa GameRepository

src/domain/interfaces/
├── __init__.py
├── user_repository.py               ← Protocol UserRepository
├── club_repository.py               ← Protocol ClubRepository
├── player_repository.py             ← Protocol PlayerRepository
└── game_repository.py               ← Protocol GameRepository

tests/integration/
└── test_repositories.py
```

---

**Clase `SQLiteManager` — Infraestructura:**

```python
# src/infrastructure/persistence/database_manager.py
import sqlite3
from pathlib import Path

class SQLiteManager:
    def __init__(self, db_path: str, schema_path: str, views_path: str):
        self._db_path = db_path
        self._schema_path = schema_path
        self._views_path = views_path
        self._connection: sqlite3.Connection | None = None

    def connect(self) -> sqlite3.Connection:
        """Abre la conexión y activa PRAGMA foreign_keys = ON."""
        # Si ya hay conexión activa, retornarla (patrón singleton de conexión)
        # Activar: self._connection.execute("PRAGMA foreign_keys = ON;")
        # Activar: self._connection.row_factory = sqlite3.Row  (acceso por nombre de columna)

    def initialize_schema(self) -> None:
        """Ejecuta schema.sql y views.sql de forma atómica con executescript()."""
        # Leer ambos archivos y ejecutarlos
        # Manejar FileNotFoundError y sqlite3.OperationalError con mensajes claros

    def load_seed(self) -> None:
        """Ejecuta seed.sql. SOLO usar en entornos de desarrollo/test."""

    def get_connection(self) -> sqlite3.Connection:
        """Retorna la conexión activa. Lanza RuntimeError si no está conectado."""

    def close(self) -> None:
        """Cierra la conexión de forma segura."""
```

> **Por qué `row_factory = sqlite3.Row`:** Permite acceder a los resultados por nombre de columna
> (`row['nombre']`) en lugar de por índice (`row[1]`), haciendo el código más legible y
> resistente a cambios en el orden de columnas.

---

**Interfaces de Dominio (Protocols):**

```python
# src/domain/interfaces/user_repository.py
from typing import Protocol
from domain.entities.usuario import Usuario

class UserRepository(Protocol):
    def get_by_email(self, email: str) -> Usuario | None: ...
    def get_by_id(self, id_usuario: int) -> Usuario | None: ...
    def save(self, usuario: Usuario) -> Usuario: ...       # retorna con id asignado
    def exists_by_email(self, email: str) -> bool: ...

# src/domain/interfaces/club_repository.py
class ClubRepository(Protocol):
    def get_all(self) -> list[Club]: ...
    def get_by_id(self, id_club: int) -> Club | None: ...
    def save(self, club: Club) -> Club: ...
    def link_user_to_club(self, id_usuario: int, id_club: int, rol: str | None) -> None: ...
    def get_clubs_by_user(self, id_usuario: int) -> list[Club]: ...

# src/domain/interfaces/player_repository.py
class PlayerRepository(Protocol):
    def search_by_dni(self, dni: str) -> Jugador | None: ...
    def get_by_id(self, id_jugador: int) -> Jugador | None: ...
    def search_by_name(self, nombre: str, apellido: str) -> list[Jugador]: ...
    def get_club_history(self, id_jugador: int) -> list[JugadorClub]: ...
    def get_active_club(self, id_jugador: int) -> Club | None: ...
    def save(self, jugador: Jugador) -> Jugador: ...
    def link_to_club(self, id_jugador: int, id_club: int, fecha_desde: str) -> None: ...

# src/domain/interfaces/game_repository.py
class GameRepository(Protocol):
    def save_partido(self, partido: Partido) -> Partido: ...
    def save_boxscore(self, stats: list[EstadisticaJugador], connection) -> None: ...
    # ↑ recibe la conexión para ejecutar en la misma transacción que save_partido
    def get_partidos_by_club(self, id_club: int) -> list[dict]: ...
    # ↑ consulta v_partidos_resumen, retorna lista de dicts
    def get_boxscore_by_partido(self, id_partido: int) -> list[dict]: ...
    # ↑ consulta v_boxscore_completo, retorna lista de dicts
```

> **Por qué `Protocol` y no `ABC`:** Los `Protocol` de Python permiten "duck typing" estructural.
> Una clase que implementa todos los métodos requeridos satisface el contrato automáticamente,
> sin necesidad de declarar herencia. Esto es más flexible para los mocks en tests.

---

**Patrón de implementación de repositorios (todos siguen el mismo patrón):**

```python
# src/infrastructure/persistence/sqlite_player_repository.py
import sqlite3
from domain.interfaces.player_repository import PlayerRepository
from domain.entities.jugador import Jugador

class SQLitePlayerRepository:  # satisface PlayerRepository sin herencia explícita
    def __init__(self, connection: sqlite3.Connection):
        self._conn = connection

    def search_by_dni(self, dni: str) -> Jugador | None:
        cursor = self._conn.execute(
            "SELECT idJugador, nombre, apellido, dni, anioNacimiento FROM jugador WHERE dni = ?",
            (dni,)
        )
        row = cursor.fetchone()
        return self._row_to_jugador(row) if row else None

    def save(self, jugador: Jugador) -> Jugador:
        cursor = self._conn.execute(
            "INSERT INTO jugador (nombre, apellido, dni, anioNacimiento) VALUES (?, ?, ?, ?)",
            (jugador.nombre, jugador.apellido, jugador.dni, jugador.anio_nacimiento)
        )
        self._conn.commit()
        return Jugador(
            id=cursor.lastrowid,
            nombre=jugador.nombre,
            apellido=jugador.apellido,
            dni=jugador.dni,
            anio_nacimiento=jugador.anio_nacimiento
        )

    def _row_to_jugador(self, row) -> Jugador:
        """Convierte una fila SQLite (sqlite3.Row) a la entidad de dominio Jugador."""
        return Jugador(
            id=row['idJugador'],
            nombre=row['nombre'],
            apellido=row['apellido'],
            dni=row['dni'],
            anio_nacimiento=row['anioNacimiento']
        )
    # ... resto de métodos
```

---

**Criterios de Aceptación:**

**AC1 — `SQLiteManager`:**

- `connect()` SIEMPRE ejecuta `PRAGMA foreign_keys = ON` al abrir la conexión.
- `connect()` configura `row_factory = sqlite3.Row`.
- Si se llama `connect()` cuando ya hay una conexión activa, retorna la misma (no abre una segunda).
- `initialize_schema()` ejecuta `schema.sql` y `views.sql` con `executescript()` en una sola llamada atómica.
- Si el archivo `.sql` no existe, lanza `FileNotFoundError` con el path del archivo.

**AC2 — Interfaces de Dominio:**

- Los cuatro archivos de interfaces están en `src/domain/interfaces/`.
- Ningún archivo en `domain/` importa de `sqlite3`, `pandas` o cualquier librería de infraestructura.
- Los `Protocol` tienen type hints completos en todos sus métodos.

**AC3 — Implementaciones SQLite:**

- Cada repositorio tiene un método privado `_row_to_<entidad>()` que convierte `sqlite3.Row` a `@dataclass`.
- El método `save()` usa `cursor.lastrowid` para retornar la entidad con el ID asignado por la DB.
- `SQLiteGameRepository.save_boxscore()` acepta la conexión como parámetro para permitir transacciones multi-tabla.

**Tests a escribir en `tests/integration/test_repositories.py`:**

```python
# Fixture: db_in_memory → SQLite :memory: con schema + seed cargados

def test_user_repository_save_and_get_by_email(db_in_memory): ...
# Guardar usuario → buscar por email → verificar que los datos coinciden

def test_user_repository_save_returns_id(db_in_memory): ...
# El usuario retornado por save() tiene id distinto de None

def test_player_repository_search_by_dni_not_found(db_in_memory): ...
# search_by_dni("99999999") retorna None sin lanzar excepción

def test_player_repository_search_by_dni_found(seeded_db): ...
# search_by_dni con DNI existente retorna Jugador con datos correctos

def test_club_repository_get_clubs_by_user(seeded_db): ...
# Retorna lista no vacía para usuario con clubes vinculados

def test_game_repository_get_partidos_returns_view_data(seeded_db): ...
# Retorna dicts con clave "club_local" (nombre, no ID)
# Verifica que usa v_partidos_resumen

def test_game_repository_get_boxscore_returns_player_names(seeded_db): ...
# Retorna dicts con clave "nombre_jugador"
# Verifica que usa v_boxscore_completo
```

---

### Épica E2: Lógica de Aplicación y CLI

---

#### US-103: Entidades de Dominio

**Narrativa:** Como desarrollador, quiero las entidades del básquet como `@dataclass` puras de Python, sin dependencias externas, para usarlas en toda la arquitectura.

**Dependencias previas:** Ninguna. Es dominio puro.

---

**Archivos a crear:**

```text
src/domain/entities/
├── __init__.py
├── usuario.py
├── club.py
├── jugador.py
├── jugador_club.py       ← relación N:M con historial
├── competencia.py
├── inscripcion.py
├── partido.py
└── estadistica_jugador.py   ← la más importante; incluye validaciones
```

---

**Estructuras exactas de cada entidad:**

```python
# usuario.py
from dataclasses import dataclass

@dataclass
class Usuario:
    nombre: str
    email: str
    contrasena_hash: str          # NUNCA texto plano
    id: int | None = None

# club.py
@dataclass
class Club:
    nombre: str
    id: int | None = None

# jugador.py
@dataclass
class Jugador:
    nombre: str
    apellido: str
    dni: str | None = None           # str para soportar DNIs con ceros iniciales
    anio_nacimiento: int | None = None
    id: int | None = None

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"

# jugador_club.py — historial de pertenencia a clubs
@dataclass
class JugadorClub:
    id_jugador: int
    id_club: int
    fecha_desde: str              # ISO 8601: "YYYY-MM-DD"
    fecha_hasta: str | None = None  # None = vínculo activo

    @property
    def esta_activo(self) -> bool:
        return self.fecha_hasta is None

# competencia.py
@dataclass
class Competencia:
    nombre: str
    anio: int
    tipo: str | None = None
    id: int | None = None

# inscripcion.py
@dataclass
class Inscripcion:
    id_club: int
    id_categoria: int
    id_competencia: int
    id: int | None = None

# partido.py
@dataclass
class Partido:
    id_competencia: int
    fecha: str                    # ISO 8601: "YYYY-MM-DD HH:MM"
    id_club_local: int
    id_club_visitante: int
    estadio: str | None = None
    id: int | None = None

# estadistica_jugador.py
from dataclasses import dataclass, field

@dataclass
class EstadisticaJugador:
    id_jugador: int
    id_partido: int
    id_club: int
    minutos_jugados: int = 0
    puntos: int = 0
    t2c: int = 0
    t2l: int = 0
    t3c: int = 0
    t3l: int = 0
    t1c: int = 0
    t1l: int = 0
    rebotes_def: int = 0
    rebotes_of: int = 0
    asistencias: int = 0
    recuperos: int = 0
    perdidas: int = 0
    tapones_recibidos: int = 0
    tapones_realizados: int = 0
    faltas_recibidas: int = 0
    faltas_cometidas: int = 0

    def __post_init__(self):
        self._validar()

    def _validar(self) -> None:
        """Aplica las reglas de consistencia del básquet."""
        campos_no_negativos = [
            ('minutos_jugados', self.minutos_jugados),
            ('puntos', self.puntos),
            ('t2c', self.t2c), ('t2l', self.t2l),
            ('t3c', self.t3c), ('t3l', self.t3l),
            ('t1c', self.t1c), ('t1l', self.t1l),
            # ... resto de campos
        ]
        for nombre, valor in campos_no_negativos:
            if valor < 0:
                raise ValueError(f"El campo '{nombre}' no puede ser negativo. Valor: {valor}")

        if self.t2c > self.t2l:
            raise ValueError(f"T2C ({self.t2c}) no puede superar T2L ({self.t2l})")
        if self.t3c > self.t3l:
            raise ValueError(f"T3C ({self.t3c}) no puede superar T3L ({self.t3l})")
        if self.t1c > self.t1l:
            raise ValueError(f"T1C ({self.t1c}) no puede superar T1L ({self.t1l})")

    @property
    def rebotes_totales(self) -> int:
        return self.rebotes_def + self.rebotes_of

    @property
    def tiros_de_campo_convertidos(self) -> int:
        return self.t2c + self.t3c
```

---

**Criterios de Aceptación:**

**AC1 — Dominio puro:**

- Ningún archivo en `domain/entities/` tiene imports de `sqlite3`, `pandas`, `tabulate` u otras librerías externas.
- Las entidades son serializables con `dataclasses.asdict()` sin errores.

**AC2 — Validaciones en dominio:**

- `EstadisticaJugador.__post_init__` valida: convertidos ≤ lanzados para T1, T2 y T3.
- `EstadisticaJugador.__post_init__` valida que todos los campos numéricos son ≥ 0.
- Las propiedades calculadas (`rebotes_totales`, `nombre_completo`) no tienen lógica de persistencia.

**AC3 — Campos opcionales:**

- Los campos `id` de todas las entidades son `None` por default (se asignan tras la persistencia).
- `dni` y `anio_nacimiento` en `Jugador` permiten `None` para jugadores sin datos completos.

**Tests a escribir en `tests/unit/test_entities.py`:**

```python
def test_estadistica_raises_when_t2c_greater_than_t2l():
    with pytest.raises(ValueError, match="T2C"):
        EstadisticaJugador(id_jugador=1, id_partido=1, id_club=1, t2c=5, t2l=3)

def test_estadistica_raises_on_negative_points():
    with pytest.raises(ValueError, match="puntos"):
        EstadisticaJugador(id_jugador=1, id_partido=1, id_club=1, puntos=-1)

def test_estadistica_valid_with_all_zeros():
    # No debe lanzar excepción cuando todos los valores son 0
    stats = EstadisticaJugador(id_jugador=1, id_partido=1, id_club=1)
    assert stats.puntos == 0

def test_jugador_nombre_completo_property():
    j = Jugador(nombre="Juan", apellido="Pérez")
    assert j.nombre_completo == "Juan Pérez"

def test_estadistica_rebotes_totales_property():
    s = EstadisticaJugador(id_jugador=1, id_partido=1, id_club=1, rebotes_def=3, rebotes_of=2)
    assert s.rebotes_totales == 5

def test_jugador_club_esta_activo_when_fecha_hasta_is_none():
    jc = JugadorClub(id_jugador=1, id_club=1, fecha_desde="2025-01-01")
    assert jc.esta_activo is True
```

---

#### US-104: Excepciones de Dominio y Casos de Uso Administrativos

**Narrativa:** Como administrador, quiero casos de uso con lógica de negocio validada para gestionar jugadores, clubes, competencias e inscripciones.

**Dependencias previas:** US-102, US-103.

---

**Archivos a crear:**

```text
src/domain/
└── exceptions.py                                ← todas las excepciones de negocio

src/application/
├── dtos/
│   ├── jugador_dto.py
│   ├── club_dto.py
│   └── competencia_dto.py
└── use_cases/
    ├── registrar_jugador.py
    ├── crear_club.py
    ├── vincular_jugador_club.py
    ├── crear_competencia.py
    ├── inscribir_club_competencia.py
    ├── listar_clubes_usuario.py
    └── listar_jugadores_club.py

tests/unit/
└── test_use_cases_admin.py
```

---

**Excepciones de dominio (`src/domain/exceptions.py`):**

```python
# Cada excepción describe un concepto de negocio del básquet,
# no un error técnico de Python.

class DNIInvalidoError(ValueError):
    """El DNI proporcionado no es un valor numérico válido."""

class DNIYaRegistradoError(Exception):
    """Ya existe un jugador con ese DNI en el sistema."""

class JugadorNoEncontradoError(Exception):
    """No se encontró ningún jugador con los criterios dados."""

class ClubNoEncontradoError(Exception):
    """No se encontró ningún club con el ID dado."""

class CompetenciaNoEncontradaError(Exception):
    """No se encontró ninguna competencia con el ID dado."""

class VinculoActivoExistenteError(Exception):
    """El jugador ya tiene un vínculo activo con ese club."""

class EmailYaRegistradoError(Exception):
    """Ya existe un usuario con ese email."""

class CredencialesInvalidasError(Exception):
    """Email o contraseña incorrectos."""

class UsuarioNoEncontradoError(Exception):
    """No se encontró ningún usuario con ese email."""
```

---

**DTOs (Data Transfer Objects):**

```python
# src/application/dtos/jugador_dto.py
from dataclasses import dataclass

@dataclass
class RegistrarJugadorDTO:
    """Datos de entrada para registrar un jugador nuevo."""
    nombre: str
    apellido: str
    dni: str | None = None
    anio_nacimiento: int | None = None

@dataclass
class JugadorResponseDTO:
    """Datos de salida tras registrar o consultar un jugador."""
    id: int
    nombre_completo: str
    dni: str | None
    anio_nacimiento: int | None
    club_activo: str | None = None   # nombre del club, no el ID

# src/application/dtos/club_dto.py
@dataclass
class CrearClubDTO:
    nombre: str

@dataclass
class ClubResponseDTO:
    id: int
    nombre: str

# src/application/dtos/competencia_dto.py
@dataclass
class CrearCompetenciaDTO:
    nombre: str
    anio: int
    tipo: str | None = None
```

---

**Estructura de cada Caso de Uso (patrón consistente):**

```python
# src/application/use_cases/registrar_jugador.py
from domain.interfaces.player_repository import PlayerRepository
from domain.exceptions import DNIInvalidoError, DNIYaRegistradoError
from domain.entities.jugador import Jugador
from application.dtos.jugador_dto import RegistrarJugadorDTO, JugadorResponseDTO

class RegistrarJugadorUseCase:
    def __init__(self, player_repo: PlayerRepository):
        self._player_repo = player_repo

    def execute(self, dto: RegistrarJugadorDTO) -> JugadorResponseDTO:
        # 1. Validar reglas de negocio
        if dto.dni is not None:
            if not dto.dni.isnumeric():
                raise DNIInvalidoError(f"El DNI '{dto.dni}' debe contener solo números.")
            if self._player_repo.search_by_dni(dto.dni) is not None:
                raise DNIYaRegistradoError(f"Ya existe un jugador con DNI {dto.dni}.")

        # 2. Crear entidad de dominio
        jugador = Jugador(
            nombre=dto.nombre,
            apellido=dto.apellido,
            dni=dto.dni,
            anio_nacimiento=dto.anio_nacimiento
        )

        # 3. Persistir y obtener ID asignado
        jugador_guardado = self._player_repo.save(jugador)

        # 4. Retornar DTO (nunca la entidad de dominio directamente)
        return JugadorResponseDTO(
            id=jugador_guardado.id,
            nombre_completo=jugador_guardado.nombre_completo,
            dni=jugador_guardado.dni,
            anio_nacimiento=jugador_guardado.anio_nacimiento
        )
```

---

**Lógica de negocio por caso de uso:**

`VincularJugadorAClubUseCase.execute(id_jugador, id_club, fecha_desde)`:

1. Verificar que el jugador existe → `JugadorNoEncontradoError` si no.
2. Verificar que el club existe → `ClubNoEncontradoError` si no.
3. Obtener historial del jugador y verificar que no hay un vínculo activo con ESE MISMO club (sin `fecha_hasta`) → `VinculoActivoExistenteError`.
4. Llamar `player_repo.link_to_club(id_jugador, id_club, fecha_desde)`.

`InscribirClubEnCompetenciaUseCase.execute(id_club, id_categoria, id_competencia)`:

1. Verificar club y competencia existen.
2. Verificar que no existe ya una inscripción para esa combinación club+competencia+categoría.
3. Crear inscripción y automáticamente crear la `listaBuenaFe` vacía asociada (relación 1:1).

---

**Criterios de Aceptación:**

**AC1 — Casos de Uso implementados:**

- Los 7 casos de uso de la lista están implementados.
- Ningún caso de uso importa `sqlite3` directamente.
- Todos los casos de uso reciben sus repositorios como dependencias en el constructor (Inyección de Dependencias).

**AC2 — DTOs como frontera entre capas:**

- Los casos de uso reciben DTOs como entrada y retornan DTOs como salida.
- La capa de UI (CLI) NUNCA manipula entidades de dominio (`Jugador`, `Club`) directamente; solo trabaja con DTOs.
- Las entidades de dominio no "escapan" de la capa de aplicación hacia la capa UI.

**AC3 — Excepciones de dominio:**

- Todos los casos de uso lanzan excepciones de `domain/exceptions.py`, no `ValueError` genéricos sin contexto.
- Las excepciones de dominio tienen mensajes descriptivos con el dato que causó el error.

**Tests a escribir en `tests/unit/test_use_cases_admin.py`:**

```python
# Los tests de casos de uso usan Mocks, nunca SQLite real.
# Definir clases Mock en el propio archivo de test o en conftest.py:

class MockPlayerRepository:
    """Implementa PlayerRepository usando una lista en memoria."""
    def __init__(self, jugadores_existentes: list[Jugador] = None):
        self._jugadores = jugadores_existentes or []
        self._next_id = 1

    def search_by_dni(self, dni: str) -> Jugador | None:
        return next((j for j in self._jugadores if j.dni == dni), None)

    def save(self, jugador: Jugador) -> Jugador:
        saved = Jugador(id=self._next_id, nombre=jugador.nombre, ...)
        self._jugadores.append(saved)
        self._next_id += 1
        return saved
    # ... otros métodos retornan None o lista vacía por default


def test_registrar_jugador_raises_on_duplicate_dni():
    repo = MockPlayerRepository([Jugador(id=1, nombre="X", apellido="Y", dni="12345678")])
    uc = RegistrarJugadorUseCase(repo)
    with pytest.raises(DNIYaRegistradoError):
        uc.execute(RegistrarJugadorDTO(nombre="A", apellido="B", dni="12345678"))

def test_registrar_jugador_raises_on_non_numeric_dni():
    repo = MockPlayerRepository()
    uc = RegistrarJugadorUseCase(repo)
    with pytest.raises(DNIInvalidoError):
        uc.execute(RegistrarJugadorDTO(nombre="A", apellido="B", dni="AB123"))

def test_registrar_jugador_success_returns_dto_with_id():
    repo = MockPlayerRepository()
    uc = RegistrarJugadorUseCase(repo)
    result = uc.execute(RegistrarJugadorDTO(nombre="Juan", apellido="García", dni="11222333"))
    assert result.id is not None
    assert result.nombre_completo == "Juan García"

def test_vincular_jugador_raises_when_player_not_found():
    player_repo = MockPlayerRepository()  # vacío
    club_repo = MockClubRepository([Club(id=1, nombre="Club A")])
    uc = VincularJugadorAClubUseCase(player_repo, club_repo)
    with pytest.raises(JugadorNoEncontradoError):
        uc.execute(id_jugador=999, id_club=1, fecha_desde="2025-01-01")

def test_vincular_jugador_raises_on_active_link():
    # Jugador ya tiene vínculo activo con el club
    ...
```

---

#### US-105: Caso de Uso CargarPartido (Transacción Atómica)

**Narrativa:** Como DT, quiero registrar un partido completo con todas las estadísticas de los jugadores en una única operación; si falla una sola estadística, nada se persiste.

**Dependencias previas:** US-103, US-104.

---

**Archivos a crear:**

```text
src/application/
├── dtos/partido_dto.py                  ← DTOs de entrada y salida del partido
└── use_cases/cargar_partido.py          ← CargarPartidoUseCase

tests/unit/
└── test_use_case_cargar_partido.py
```

---

**DTOs del partido:**

```python
# src/application/dtos/partido_dto.py
from dataclasses import dataclass, field

@dataclass
class EstadisticaInputDTO:
    """Estadísticas de un jugador en un partido. Entrada desde la UI."""
    id_jugador: int
    minutos_jugados: int
    puntos: int
    t2c: int; t2l: int
    t3c: int; t3l: int
    t1c: int; t1l: int
    rebotes_def: int; rebotes_of: int
    asistencias: int
    recuperos: int
    perdidas: int
    tapones_recibidos: int
    tapones_realizados: int
    faltas_recibidas: int
    faltas_cometidas: int

@dataclass
class CargarPartidoDTO:
    """Datos completos para cargar un partido con su boxscore."""
    id_competencia: int
    fecha: str                                         # "YYYY-MM-DD"
    id_club_local: int
    id_club_visitante: int
    estadisticas_local: list[EstadisticaInputDTO] = field(default_factory=list)
    estadisticas_visitante: list[EstadisticaInputDTO] = field(default_factory=list)
    estadio: str | None = None

@dataclass
class PartidoCargadoResponseDTO:
    """Confirmación tras cargar el partido exitosamente."""
    id_partido: int
    fecha: str
    club_local: str
    club_visitante: str
    total_jugadores_cargados: int
```

---

**Lógica del caso de uso `CargarPartidoUseCase`:**

```python
class CargarPartidoUseCase:
    def __init__(self, game_repo: GameRepository, club_repo: ClubRepository):
        self._game_repo = game_repo
        self._club_repo = club_repo

    def execute(self, dto: CargarPartidoDTO) -> PartidoCargadoResponseDTO:
        # 1. Validar que local != visitante
        if dto.id_club_local == dto.id_club_visitante:
            raise ValueError("El club local y visitante no pueden ser el mismo.")

        # 2. Crear entidad Partido
        partido = Partido(
            id_competencia=dto.id_competencia,
            fecha=dto.fecha,
            id_club_local=dto.id_club_local,
            id_club_visitante=dto.id_club_visitante,
            estadio=dto.estadio
        )

        # 3. Convertir DTOs a entidades EstadisticaJugador
        #    La construcción de EstadisticaJugador dispara __post_init__ con validaciones.
        #    Si algún DTO tiene datos inválidos, se lanza ValueError ANTES de tocar la DB.
        todas_las_stats: list[EstadisticaJugador] = []
        for est_dto in dto.estadisticas_local:
            stats = EstadisticaJugador(
                id_jugador=est_dto.id_jugador,
                id_partido=0,  # placeholder, se reemplaza tras save_partido
                id_club=dto.id_club_local,
                # ... mapear todos los campos
            )
            todas_las_stats.append(stats)
        # Repetir para estadisticas_visitante con id_club=dto.id_club_visitante

        # 4. Persistir en transacción atómica:
        #    a) save_partido → obtener id_partido
        #    b) Actualizar id_partido en todas las stats
        #    c) save_boxscore (todas las filas en una sola transacción)
        partido_guardado = self._game_repo.save_partido(partido)
        for stats in todas_las_stats:
            stats.id_partido = partido_guardado.id
        self._game_repo.save_boxscore(todas_las_stats)

        # Si save_boxscore falla, save_partido ya fue commiteado...
        # ↑ DECISIÓN DE DISEÑO A DOCUMENTAR: usar transacciones explícitas
        #   o dejar que el repositorio maneje el rollback.
        #   Opción recomendada: pasar la conexión sin autocommit y hacer commit
        #   solo al final (ver implementación en sqlite_game_repository.py).
```

> **Nota de implementación crítica:** Para garantizar atomicidad, `SQLiteGameRepository`
> debe recibir la conexión sin autocommit y hacer `connection.commit()` solo al final
> de `save_boxscore()`. Si falla, debe llamar `connection.rollback()`.
> Investigar: transacciones explícitas en `sqlite3` de Python con `with connection:`.

---

**Criterios de Aceptación:**

**AC1 — Atomicidad garantizada:**

- Si una `EstadisticaJugador` falla la validación de `__post_init__`, NINGÚN dato se persiste.
- Si la inserción de una estadística en la DB falla (ej: FK inválida), se hace rollback completo del partido y todas las estadísticas anteriores.

**AC2 — Validaciones pre-persistencia:**

- La validación de los DTOs ocurre ANTES de la primera operación de base de datos.
- El mensaje de error especifica qué jugador y qué campo causó el error.

**Tests a escribir:**

```python
def test_cargar_partido_rechaza_mismo_club_local_y_visitante():
    uc = CargarPartidoUseCase(MockGameRepo(), MockClubRepo())
    with pytest.raises(ValueError, match="mismo"):
        uc.execute(CargarPartidoDTO(id_competencia=1, fecha="2025-01-01",
                                    id_club_local=1, id_club_visitante=1))

def test_cargar_partido_no_persiste_si_estadistica_invalida():
    # Si un DTO tiene T2C > T2L, nada debe haberse guardado
    mock_repo = MockGameRepo()
    uc = CargarPartidoUseCase(mock_repo, MockClubRepo())
    dto_invalido = CargarPartidoDTO(...)  # con estadística inválida
    with pytest.raises(ValueError):
        uc.execute(dto_invalido)
    assert mock_repo.partidos_guardados == 0  # verificar que no se guardó nada

def test_cargar_partido_exitoso_retorna_dto_con_id():
    uc = CargarPartidoUseCase(MockGameRepo(), MockClubRepo())
    result = uc.execute(dto_valido)
    assert result.id_partido is not None
    assert result.total_jugadores_cargados == len(dto_valido.estadisticas_local) + len(dto_valido.estadisticas_visitante)
```

---

#### US-106: Autenticación y Sesión Local

**Narrativa:** Como usuario, quiero un sistema de login local que proteja mis datos y mantenga mi sesión entre ejecuciones de la CLI.

**Dependencias previas:** US-102, US-103.

---

**Archivos a crear:**

```text
src/infrastructure/security/
└── password_hasher.py               ← PasswordHasher (estático)

src/application/
├── services/session_manager.py      ← SessionManager
└── use_cases/
    ├── registrar_entrenador.py      ← RegistrarEntrenadorUseCase
    └── login_local.py               ← LoginLocalUseCase

src/application/dtos/
└── auth_dto.py                      ← RegistrarDTO, LoginDTO, SessionDTO

tests/unit/
└── test_auth.py
```

---

**`PasswordHasher` — Infraestructura de seguridad:**

```python
# src/infrastructure/security/password_hasher.py
import hashlib

class PasswordHasher:
    # Salt estático para v0.1. DOCUMENTAR como limitación de seguridad conocida.
    # En v1.5 migrar a bcrypt con salt dinámico por usuario.
    _SALT = "statspro_basketball_v1_salt"

    @staticmethod
    def hash(plain_password: str) -> str:
        """Retorna el hash SHA-256 de la contraseña con salt."""
        salted = f"{PasswordHasher._SALT}{plain_password}"
        return hashlib.sha256(salted.encode('utf-8')).hexdigest()

    @staticmethod
    def verify(plain_password: str, stored_hash: str) -> bool:
        """Retorna True si la contraseña coincide con el hash almacenado."""
        return PasswordHasher.hash(plain_password) == stored_hash
```

---

**`SessionManager` — Servicio de aplicación:**

```python
# src/application/services/session_manager.py
import json
from pathlib import Path

class SessionManager:
    SESSION_FILE = Path.home() / ".statspro_session.json"
    # Guardar en el home del usuario, no en el directorio del proyecto.
    # Esto evita que el archivo quede en el repositorio git.

    def save_session(self, id_usuario: int, id_club: int | None = None) -> None:
        """Persiste la sesión activa en disco."""
        data = {"usuario_id": id_usuario, "club_id": id_club}
        self.SESSION_FILE.write_text(json.dumps(data), encoding='utf-8')

    def load_session(self) -> dict | None:
        """Carga la sesión desde disco. Retorna None si no existe."""
        if not self.SESSION_FILE.exists():
            return None
        return json.loads(self.SESSION_FILE.read_text(encoding='utf-8'))

    def set_active_club(self, id_club: int) -> None:
        """Actualiza solo el club activo en la sesión existente."""
        session = self.load_session()
        if session is None:
            raise RuntimeError("No hay sesión activa. Inicia sesión primero.")
        session["club_id"] = id_club
        self.SESSION_FILE.write_text(json.dumps(session), encoding='utf-8')

    def clear_session(self) -> None:
        """Elimina el archivo de sesión (logout)."""
        if self.SESSION_FILE.exists():
            self.SESSION_FILE.unlink()

    def is_authenticated(self) -> bool:
        return self.load_session() is not None

    def get_current_user_id(self) -> int | None:
        session = self.load_session()
        return session["usuario_id"] if session else None

    def get_active_club_id(self) -> int | None:
        session = self.load_session()
        return session.get("club_id") if session else None
```

---

**Lógica de los casos de uso:**

`RegistrarEntrenadorUseCase.execute(dto: RegistrarDTO)`:

1. Verificar email no duplicado → `EmailYaRegistradoError`.
2. Hashear contraseña: `PasswordHasher.hash(dto.contrasena)`.
3. Crear `Usuario(nombre, email, contrasena_hash=hash)`.
4. Persistir vía `user_repo.save()`.
5. Retornar `SessionDTO` con datos del usuario creado.

`LoginLocalUseCase.execute(dto: LoginDTO)`:

1. Buscar por email → `UsuarioNoEncontradoError` si no existe.
2. Verificar hash → `CredencialesInvalidasError` si no coincide.
3. Llamar `session_manager.save_session(usuario.id)`.
4. Retornar `SessionDTO` con `usuario_id` y `nombre`.

---

**Criterios de Aceptación:**

**AC1 — Seguridad:**

- Las contraseñas NUNCA se almacenan ni se loggean en texto plano en ningún lugar del código.
- El archivo `.statspro_session.json` solo contiene IDs enteros, no tokens ni contraseñas.
- `PasswordHasher.hash()` es determinista: el mismo input siempre da el mismo output.

**AC2 — Sesión persistente:**

- Al reiniciar la CLI, `session_manager.is_authenticated()` retorna `True` si había sesión activa.
- `set_active_club()` falla con error descriptivo si no hay sesión previa.
- `clear_session()` no lanza error si no existe el archivo (operación idempotente).

**Tests a escribir:**

```python
def test_login_falla_con_password_incorrecto(mock_user_repo, session_manager):
    with pytest.raises(CredencialesInvalidasError):
        LoginLocalUseCase(mock_user_repo, session_manager).execute(
            LoginDTO(email="test@test.com", contrasena="wrong_password")
        )

def test_login_falla_con_email_inexistente(mock_user_repo, session_manager):
    with pytest.raises(UsuarioNoEncontradoError): ...

def test_sesion_persiste_entre_ejecuciones(tmp_path, monkeypatch):
    # Usar monkeypatch para cambiar SESSION_FILE al tmp_path
    sm = SessionManager()
    sm.save_session(id_usuario=42, id_club=7)
    # Simular "nueva ejecución" creando nueva instancia
    sm2 = SessionManager()
    assert sm2.get_current_user_id() == 42
    assert sm2.get_active_club_id() == 7

def test_password_hasher_es_determinista():
    h1 = PasswordHasher.hash("mi_password")
    h2 = PasswordHasher.hash("mi_password")
    assert h1 == h2

def test_password_hasher_verify_correct():
    h = PasswordHasher.hash("abc123")
    assert PasswordHasher.verify("abc123", h) is True
    assert PasswordHasher.verify("abc124", h) is False

def test_registrar_entrenador_rechaza_email_duplicado(mock_user_repo):
    mock_user_repo.set_existing_email("test@test.com")
    with pytest.raises(EmailYaRegistradoError): ...
```

---

#### US-107: Interfaz CLI con Command Pattern

**Narrativa:** Como administrador, quiero una CLI estructurada con subcomandos claros para gestionar todas las entidades, que muestre los datos en tablas formateadas.

**Dependencias previas:** US-104, US-105, US-106.

---

**Archivos a crear:**

```text
src/infrastructure/ui/cli/
├── main_cli.py                     ← punto de entrada, registra todos los subcomandos
├── commands/
│   ├── __init__.py
│   ├── auth_commands.py            ← register, login, logout
│   ├── club_commands.py            ← add, list, select
│   ├── player_commands.py          ← add, list, link
│   └── game_commands.py            ← add (formulario interactivo), list, boxscore
└── formatters/
    └── table_formatter.py          ← TableFormatter (wrapper de tabulate)
```

---

**Estructura de comandos (usar `argparse`):**

```text
stats auth register
stats auth login
stats auth logout

stats club add                      → solicita nombre por input()
stats club list                     → tabla con v_partidos_resumen (filtrado por usuario)
stats club select <id>              → actualiza sesión

stats player add                    → formulario interactivo campo por campo
stats player list                   → tabla: ID | Nombre | DNI | Club Activo
stats player link <id_jugador>      → solicita id_club y fecha_desde

stats game add                      → formulario multi-paso (ver detalle abajo)
stats game list                     → tabla con v_partidos_resumen
stats game boxscore <id_partido>    → tabla con v_boxscore_completo
```

---

**`TableFormatter` — wrapper de `tabulate`:**

```python
# src/infrastructure/ui/cli/formatters/table_formatter.py
from tabulate import tabulate

class TableFormatter:
    DEFAULT_FORMAT = "rounded_outline"

    @staticmethod
    def print_table(data: list[dict], title: str = "") -> None:
        """Imprime una lista de dicts como tabla formateada."""
        if not data:
            print("  (Sin resultados)")
            return
        if title:
            print(f"\n  {title}")
        print(tabulate(data, headers="keys", tablefmt=TableFormatter.DEFAULT_FORMAT))
        print()

    @staticmethod
    def print_boxscore(data: list[dict]) -> None:
        """Imprime boxscore con columnas específicas de básquet."""
        columnas = ['nombre_jugador', 'nombre_club', 'minutosJugados',
                    'puntos', 'T2C', 'T2L', 'T3C', 'T3L', 'T1C', 'T1L',
                    'rebotes_totales', 'asistencias', 'recuperos', 'perdidas']
        datos_filtrados = [{k: row[k] for k in columnas if k in row} for row in data]
        TableFormatter.print_table(datos_filtrados, title="Box Score del Partido")
```

---

**Formulario interactivo para `game add` — flujo paso a paso:**

```text
$ stats game add

  === CARGAR NUEVO PARTIDO ===

  Competencias disponibles:
  [1] Liga Provincial 2025
  Seleccionar competencia (número): 1

  Fecha del partido (YYYY-MM-DD): 2025-07-15

  Clubes disponibles (tu cuenta):
  [1] Club Atletico Norte
  [2] Club Deportivo Sur
  Club LOCAL (número): 1
  Club VISITANTE (número): 2

  Estadio (dejar vacío para omitir): Estadio Municipal

  === ESTADÍSTICAS - CLUB LOCAL: Club Atletico Norte ===
  (Lista de jugadores habilitados para esta competencia)

  [1] Juan García  [2] Pedro López  ...
  ¿Agregar estadísticas? (s/n): s
  Jugador (número): 1

  Juan García:
    Minutos jugados: 28
    Puntos: 14
    T2 Conv/Lanz (ej: 4/7): 4/7
    T3 Conv/Lanz (ej: 2/5): 2/5
    T1 Conv/Lanz (ej: 0/0): 0/0
    Rebotes Def/Of (ej: 3/1): 3/1
    Asistencias: 4
    Recuperos: 2
    Pérdidas: 1
    Tapones Recib/Real (ej: 0/1): 0/1
    Faltas Recib/Comet (ej: 2/3): 2/3

  ¿Agregar otro jugador del Club Local? (s/n): s
  ...
  ¿Agregar otro jugador del Club Local? (s/n): n

  === ESTADÍSTICAS - CLUB VISITANTE: Club Deportivo Sur ===
  ...

  ¿Confirmar carga del partido? (s/n): s
  ✓ Partido cargado exitosamente (ID: 5)
```

---

**Manejo de errores en la CLI:**

```python
# En cada comando, las excepciones de dominio se capturan y muestran
# como mensajes amigables, SIN mostrar el traceback al usuario.

try:
    result = use_case.execute(dto)
    print(f"✓ {result}")
except DNIYaRegistradoError as e:
    print(f"✗ Error: {e}")
except DNIInvalidoError as e:
    print(f"✗ El DNI ingresado es inválido: {e}")
except Exception as e:
    print(f"✗ Error inesperado: {e}")
    # En modo debug (variable de entorno), mostrar traceback completo
```

---

**Guard de sesión (verificación antes de cada comando):**

```python
def require_auth(session_manager: SessionManager) -> int:
    """
    Verifica que hay sesión activa. Retorna el id_usuario.
    Llama a sys.exit(1) con mensaje si no hay sesión.
    """
    if not session_manager.is_authenticated():
        print("✗ Debes iniciar sesión primero. Usa: stats auth login")
        sys.exit(1)
    return session_manager.get_current_user_id()

def require_active_club(session_manager: SessionManager) -> int:
    """Además de auth, verifica que hay un club activo seleccionado."""
    require_auth(session_manager)
    club_id = session_manager.get_active_club_id()
    if club_id is None:
        print("✗ Debes seleccionar un club activo. Usa: stats club select <id>")
        sys.exit(1)
    return club_id
```

---

**Criterios de Aceptación:**

**AC1 — Command Pattern:**

- Agregar un nuevo grupo de comandos (ej: `stats competition ...`) solo requiere crear un nuevo archivo en `commands/` y registrarlo en `main_cli.py`. No se modifica ningún otro archivo.
- Las excepciones de dominio nunca muestran tracebacks al usuario final.

**AC2 — Visualización con vistas SQL:**

- `stats game list` usa los datos de `v_partidos_resumen` (nombres de clubs, no IDs).
- `stats game boxscore <id>` usa `v_boxscore_completo` y muestra tabla formateada con `TableFormatter`.
- `stats player list` muestra el club activo del jugador (del historial `jugadorClub`).

**AC3 — Flujo de sesión:**

- Los comandos `club`, `player` y `game` ejecutan `require_auth()` al inicio.
- Los comandos `game` y `player list` ejecutan `require_active_club()`.

---

## HITO 2: Motor de Ingesta y Análisis (v0.2)

**Decisión previa requerida:** ADR-002 debe estar aprobado (elección del framework UI: Flet vs Compose Multiplatform).

---

### Épica E3: GUI Base e Inteligencia Deportiva

---

#### US-201: Motor Estadístico con Pandas

**Narrativa:** Como DT, quiero que el sistema calcule métricas avanzadas (eFG%, EFF, PPP) automáticamente a partir de los datos cargados.

**Dependencias previas:** US-101 (vistas SQL), US-102 (repositorios).

---

**Archivos a crear:**

```text
src/infrastructure/analytics/
├── formulas.py           ← funciones puras de cálculo estadístico (sin DB)
└── analytics_service.py  ← lee vistas SQL, entrega DataFrames con métricas

src/application/use_cases/
└── calcular_estadisticas_partido.py   ← CalcularEstadisticasPartidoUseCase

tests/unit/
└── test_formulas.py

tests/integration/
└── test_analytics_service.py
```

---

**`formulas.py` — funciones puras (no requieren DB):**

```python
# src/infrastructure/analytics/formulas.py
import pandas as pd
import numpy as np

def calcular_efg(df: pd.DataFrame) -> pd.Series:
    """
    Effective Field Goal Percentage.
    Fórmula: eFG% = (T2C + 1.5 * T3C) / (T2L + T3L)
    Los tiros de 3 puntos valen más que los de 2; normaliza por eso.
    Retorna 0.0 cuando no hay tiros intentados.
    """
    total_lanzados = df['T2L'] + df['T3L']
    return np.where(
        total_lanzados > 0,
        (df['T2C'] + 1.5 * df['T3C']) / total_lanzados,
        0.0
    )

def calcular_efficiency(df: pd.DataFrame) -> pd.Series:
    """
    Efficiency (EFF) — métrica NBA de rendimiento global por partido.
    Fórmula: EFF = PTS + REB + AST + REC + TAP_REAL
                   - (T2L-T2C) - (T3L-T3C) - (T1L-T1C) - PERD
    """
    tiros_fallados = (df['T2L'] - df['T2C']) + (df['T3L'] - df['T3C']) + (df['T1L'] - df['T1C'])
    return (
        df['puntos']
        + (df['rebotesDef'] + df['rebotesOf'])
        + df['asistencias']
        + df['recuperos']
        + df['taponesRealizados']
        - tiros_fallados
        - df['perdidas']
    )

def calcular_ppp(puntos_totales: int, posesiones: int) -> float:
    """
    Points Per Possession — eficiencia ofensiva del equipo.
    Fórmula: PPP = puntos_totales / posesiones
    Las posesiones se estiman: T2L + T3L + (T1L / 2) + perdidas - rebotes_of
    """
    if posesiones == 0:
        return 0.0
    return round(puntos_totales / posesiones, 3)

def aplicar_metricas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica todas las métricas al DataFrame de boxscore.
    Retorna una copia del DataFrame con columnas adicionales.
    Las columnas originales no se modifican.
    """
    resultado = df.copy()
    resultado['eFG%'] = calcular_efg(df)
    resultado['EFF'] = calcular_efficiency(df)
    return resultado
```

---

**`AnalyticsService` — lee vistas SQL:**

```python
# src/infrastructure/analytics/analytics_service.py
import sqlite3
import pandas as pd
from infrastructure.analytics.formulas import aplicar_metricas

class AnalyticsService:
    def __init__(self, connection: sqlite3.Connection):
        self._conn = connection

    def get_boxscore_dataframe(self, id_partido: int) -> pd.DataFrame:
        """Lee v_boxscore_completo para un partido específico."""
        query = "SELECT * FROM v_boxscore_completo WHERE idPartido = ?"
        return pd.read_sql_query(query, self._conn, params=(id_partido,))

    def get_season_totals_dataframe(self, id_club: int | None = None, anio: int | None = None) -> pd.DataFrame:
        """Lee v_jugador_totales_temporada con filtros opcionales."""
        query = "SELECT * FROM v_jugador_totales_temporada"
        params = []
        conditions = []
        if anio:
            conditions.append("anio = ?")
            params.append(anio)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        return pd.read_sql_query(query, self._conn, params=params)

    def calcular_metricas_partido(self, id_partido: int) -> pd.DataFrame:
        """Retorna el boxscore enriquecido con métricas calculadas."""
        df = self.get_boxscore_dataframe(id_partido)
        if df.empty:
            return df
        return aplicar_metricas(df)
```

---

**Criterios de Aceptación:**

**AC1 — `formulas.py` es puro:**

- Ninguna función en `formulas.py` importa `sqlite3` ni accede a la DB.
- Todas las funciones aceptan `pd.DataFrame` y retornan `pd.Series` o `pd.DataFrame`.
- La cobertura de tests de `formulas.py` debe ser del 100%.

**AC2 — División por cero protegida:**

- `calcular_efg()` retorna `0.0` (no `NaN`, no `inf`) cuando `T2L + T3L = 0`.
- `calcular_ppp()` retorna `0.0` cuando `posesiones = 0`.

**AC3 — `AnalyticsService` usa las vistas SQL:**

- `get_boxscore_dataframe()` lee exclusivamente de `v_boxscore_completo`, no de `jugadorPartido` directamente.
- `get_season_totals_dataframe()` lee de `v_jugador_totales_temporada`.
- Los nombres de columna en los DataFrames coinciden con los definidos en las vistas.

**Tests a escribir:**

```python
# tests/unit/test_formulas.py
def test_efg_returns_zero_when_no_shots_taken():
    df = pd.DataFrame([{'T2C': 0, 'T2L': 0, 'T3C': 0, 'T3L': 0}])
    result = calcular_efg(df)
    assert result[0] == 0.0

def test_efg_calculates_correctly():
    # T2C=4, T2L=8, T3C=2, T3L=5 → eFG = (4 + 1.5*2) / (8+5) = 7/13 ≈ 0.538
    df = pd.DataFrame([{'T2C': 4, 'T2L': 8, 'T3C': 2, 'T3L': 5}])
    result = calcular_efg(df)
    assert abs(result[0] - 0.538) < 0.001

def test_efficiency_with_known_values():
    # Calcular manualmente y verificar contra la función
    df = pd.DataFrame([{
        'puntos': 20, 'rebotesDef': 5, 'rebotesOf': 2, 'asistencias': 4,
        'recuperos': 2, 'taponesRealizados': 1, 'perdidas': 3,
        'T2L': 8, 'T2C': 5, 'T3L': 4, 'T3C': 2, 'T1L': 4, 'T1C': 4
    }])
    # EFF = 20 + 7 + 4 + 2 + 1 - (3 + 2 + 0) - 3 = 34 - 5 - 3 = 26
    result = calcular_efficiency(df)
    assert result[0] == 26

def test_aplicar_metricas_adds_columns_without_modifying_originals():
    df_original = pd.DataFrame([{'T2C': 3, 'T2L': 6, 'T3C': 1, 'T3L': 3, ...}])
    df_resultado = aplicar_metricas(df_original)
    assert 'eFG%' in df_resultado.columns
    assert 'EFF' in df_resultado.columns
    # Verificar que el original no fue modificado
    assert 'eFG%' not in df_original.columns
```

---

### Épica E4: Ingesta Multimodal

---

#### US-202: Importación de Excel (Ges Deportivo)

**Narrativa:** Como analista, quiero importar planillas Excel de Ges Deportivo para que las estadísticas se procesen automáticamente sin re-ingresar datos.

**Dependencias previas:** US-104 (casos de uso admin), US-105 (cargar partido).

---

**Investigación requerida antes de implementar:**

> Antes de implementar el parser, un desarrollador debe obtener una planilla Excel real de Ges Deportivo y documentar en un comentario al inicio de `excel_parser.py`:
>
> - Los nombres exactos de las columnas.
> - El formato de las fechas.
> - Cómo se identifican los jugadores (nombre completo, DNI, número de camiseta).
> - Si hay columnas de totales que deben ignorarse.

---

**Archivos a crear:**

```text
src/infrastructure/ingest/
├── excel_parser.py      ← GesDeportivoExcelParser
└── ingest_service.py    ← IngestService (lógica de merge)

src/application/
├── dtos/ingest_dto.py   ← IngestRowDTO, IngestResultDTO
└── use_cases/importar_excel.py   ← ImportarExcelUseCase

src/domain/exceptions.py   ← agregar: InvalidExcelFormatError

tests/unit/
└── test_excel_ingest.py
```

---

**DTOs de ingesta:**

```python
# src/application/dtos/ingest_dto.py
from dataclasses import dataclass, field

@dataclass
class IngestRowDTO:
    """Representa una fila del Excel ya parseada y normalizada."""
    nombre_jugador: str
    apellido_jugador: str
    nombre_club: str
    fecha_partido: str        # ISO: "YYYY-MM-DD"
    puntos: int
    t2c: int; t2l: int
    t3c: int; t3l: int
    t1c: int; t1l: int
    rebotes_def: int; rebotes_of: int
    asistencias: int
    recuperos: int; perdidas: int
    tapones_recibidos: int; tapones_realizados: int
    faltas_recibidas: int; faltas_cometidas: int
    minutos_jugados: int = 0
    dni: str | None = None    # si el Excel lo incluye

@dataclass
class IngestResultDTO:
    """Resumen del resultado de la importación."""
    partidos_creados: int
    jugadores_creados: int        # jugadores nuevos que no existían en la DB
    jugadores_encontrados: int    # jugadores ya existentes, reutilizados
    filas_procesadas: int
    errores: list[str] = field(default_factory=list)
    advertencias: list[str] = field(default_factory=list)
```

---

**`GesDeportivoExcelParser`:**

```python
class GesDeportivoExcelParser:
    # Documentar aquí las columnas reales del Excel de Ges Deportivo
    # tras investigación. Ejemplo placeholder:
    EXPECTED_COLUMNS = {
        'Jugador', 'Club', 'Fecha', 'PTS',
        'T2C', 'T2L', 'T3C', 'T3L', 'TLC', 'TLL',
        'RD', 'RO', 'AS', 'REC', 'PERD', 'TP'
    }

    def __init__(self, file_path: str):
        self._path = file_path

    def parse(self) -> list[IngestRowDTO]:
        df = pd.read_excel(self._path)
        self._validate_columns(df)
        rows = []
        for _, row in df.iterrows():
            try:
                rows.append(self._row_to_dto(row))
            except (ValueError, KeyError) as e:
                # Log advertencia y continuar, no abortar todo el proceso
                raise  # por ahora re-raise; en v1.0 acumular advertencias
        return rows

    def _validate_columns(self, df: pd.DataFrame) -> None:
        missing = self.EXPECTED_COLUMNS - set(df.columns)
        if missing:
            raise InvalidExcelFormatError(
                f"El archivo Excel no tiene el formato esperado de Ges Deportivo. "
                f"Columnas faltantes: {', '.join(sorted(missing))}"
            )

    def _row_to_dto(self, row) -> IngestRowDTO:
        # Separar nombre completo en nombre + apellido (si es una sola columna)
        # Limpiar valores NaN con: int(row['PTS']) if pd.notna(row['PTS']) else 0
        ...
```

---

**`IngestService` — lógica de merge:**

```python
class IngestService:
    def __init__(self, player_repo: PlayerRepository, game_repo: GameRepository,
                 club_repo: ClubRepository):
        self._player_repo = player_repo
        self._game_repo = game_repo
        self._club_repo = club_repo

    def process_rows(self, rows: list[IngestRowDTO], id_competencia: int) -> IngestResultDTO:
        """
        Procesa las filas del Excel y las persiste.
        Estrategia de merge para jugadores:
          1. Buscar por DNI si está disponible.
          2. Si no, buscar por nombre+apellido exacto (case-insensitive).
          3. Si no se encuentra → crear nuevo jugador automáticamente.
        """
        resultado = IngestResultDTO(0, 0, 0, len(rows))
        # Agrupar filas por partido (misma fecha + mismo par de clubes)
        # Para cada grupo → crear Partido y llamar CargarPartidoUseCase
        ...
```

---

**`ImportarExcelUseCase` — con preview pre-commit:**

```python
class ImportarExcelUseCase:
    def __init__(self, parser: GesDeportivoExcelParser, ingest_service: IngestService):
        ...

    def preview(self, file_path: str) -> list[IngestRowDTO]:
        """Parsea el archivo y retorna los datos SIN persistir nada."""
        parser = GesDeportivoExcelParser(file_path)
        return parser.parse()

    def execute(self, file_path: str, id_competencia: int) -> IngestResultDTO:
        """Parsea Y persiste los datos."""
        rows = self.preview(file_path)
        return self._ingest_service.process_rows(rows, id_competencia)
```

---

**Criterios de Aceptación:**

**AC1 — Validación del formato:**

- El parser lanza `InvalidExcelFormatError` con la lista de columnas faltantes si el archivo no tiene el formato esperado.
- El error ocurre ANTES de procesar cualquier fila (fail-fast).

**AC2 — Lógica de merge:**

- Si el jugador no existe en la DB, se crea automáticamente y `jugadores_creados` se incrementa.
- Si el jugador ya existe (por DNI o nombre), se reutiliza y `jugadores_encontrados` se incrementa.
- Nunca se crean dos jugadores con el mismo DNI durante la importación.

**AC3 — Preview sin persistencia:**

- `preview()` puede llamarse múltiples veces sin efectos secundarios en la DB.
- `execute()` solo persiste si `preview()` no lanzó excepciones.

**Tests a escribir:**

```python
def test_parser_raises_on_missing_columns(tmp_excel_wrong_format):
    with pytest.raises(InvalidExcelFormatError, match="Columnas faltantes"):
        GesDeportivoExcelParser(tmp_excel_wrong_format).parse()

def test_ingest_creates_new_player_when_not_found(mock_repos):
    rows = [IngestRowDTO(nombre_jugador="Nuevo", apellido_jugador="Jugador", ...)]
    service = IngestService(*mock_repos)
    result = service.process_rows(rows, id_competencia=1)
    assert result.jugadores_creados == 1
    assert result.jugadores_encontrados == 0

def test_ingest_reuses_existing_player_by_name(mock_repos):
    # mock_repos tiene "Nuevo Jugador" ya en la DB
    result = service.process_rows(rows, id_competencia=1)
    assert result.jugadores_creados == 0
    assert result.jugadores_encontrados == 1

def test_preview_does_not_call_save_on_repos(mock_repos):
    uc = ImportarExcelUseCase(parser, IngestService(*mock_repos))
    uc.preview("archivo_valido.xlsx")
    assert mock_repos[0].save_call_count == 0  # player_repo.save() nunca llamado
```

---

## HITO 3: Visualización y Entrega (v1.0)

**Decisiones previas requeridas:**

- ADR-005: Librería para PDF (recomendación: `reportlab` o `weasyprint`).
- ADR-007: Motor de visualización (recomendación: `matplotlib` embebido en Flet, o `plotly`).

---

### Épica E5: Analítica Visual y Reporting

---

#### US-301: Dashboards e Informes Interactivos

**Narrativa:** Como DT, quiero ver gráficos de rendimiento de jugadores y equipos para planificar la táctica.

**Archivos a crear:**

```text
src/infrastructure/analytics/
└── chart_generator.py     ← ChartGenerator (genera figuras matplotlib/plotly)

src/infrastructure/ui/flet/
├── screens/
│   └── dashboard_screen.py
└── components/
    └── chart_component.py  ← wrapper para embeber gráficos en Flet
```

---

**Gráficos requeridos — `ChartGenerator`:**

```python
class ChartGenerator:
    """Genera figuras de matplotlib a partir de DataFrames del AnalyticsService."""

    def evolucion_puntos_jugador(self, df_temporada: pd.DataFrame, id_jugador: int): ...
    # Gráfico de líneas: eje X = partidos cronológicos, eje Y = puntos

    def comparativa_efg_equipo(self, df_partido: pd.DataFrame): ...
    # Gráfico de barras horizontales: jugadores vs eFG%, ordenado descendente

    def distribucion_tiros(self, df_jugador: pd.DataFrame): ...
    # Donut chart: % de puntos de T1 / T2 / T3

    def rebotes_tendencia(self, df_temporada: pd.DataFrame): ...
    # Área apilada: rebotes ofensivos vs defensivos por partido
```

---

**Criterios de Aceptación:**

**AC1 — Gráficos basados en vistas SQL:**

- Cada método de `ChartGenerator` recibe un `pd.DataFrame` (ya calculado por `AnalyticsService`), no IDs ni conexiones.
- Los gráficos se generan en menos de 2 segundos para un equipo de 15 jugadores.

**AC2 — Interactividad:**

- El usuario puede seleccionar temporada/competencia desde un dropdown.
- Al cambiar el filtro, los gráficos se regeneran automáticamente.

---

#### US-302: Exportación a PDF

**Narrativa:** Como DT, quiero exportar el box score y las métricas avanzadas a PDF para compartir con mi cuerpo técnico.

**Archivos a crear:**

```text
src/infrastructure/reports/
└── pdf_generator.py          ← PDFReportGenerator

src/application/use_cases/
└── exportar_reporte.py       ← ExportarReporteUseCase

src/application/dtos/
└── reporte_dto.py            ← TipoReporte (Enum), ExportarReporteDTO
```

---

**Tipos de reporte (`TipoReporte` Enum):**

```python
from enum import Enum

class TipoReporte(Enum):
    BOXSCORE_PARTIDO = "boxscore_partido"
    # Fuente: v_boxscore_completo. Incluye: fecha, clubes, tabla de stats por jugador.

    RESUMEN_TEMPORADA = "resumen_temporada"
    # Fuente: v_jugador_totales_temporada. Incluye: totales y promedios por jugador.

    SCOUTING_JUGADOR = "scouting_jugador"
    # Fuente: v_jugador_totales_temporada + fórmulas aplicadas.
    # Incluye: eFG%, EFF, tendencias.
```

---

**Convención de nombres de archivos PDF:**

```text
boxscore_2025-07-15_ClubNorte_vs_ClubSur.pdf
temporada_2025_ClubNorte_U17.pdf
scouting_JuanGarcia_2025.pdf
```

Los PDFs se guardan en `exports/` (configurable, relativo al directorio de trabajo).

---

**Criterios de Aceptación:**

**AC1 — Generación:**

- El PDF incluye el nombre del club y la fecha en el encabezado.
- Los datos se presentan en tablas con alineación numérica correcta (cifras a la derecha).
- Se genera en menos de 5 segundos para un boxscore de 15 jugadores.

**AC2 — Exportación:**

- El directorio `exports/` se crea automáticamente si no existe.
- El archivo sigue la convención de nombres definida.
- `ExportarReporteUseCase.execute()` retorna el path absoluto del archivo generado.

---

## Tabla de Trazabilidad: US → Artefactos

| US         | Entidades Dominio                                                             | Interfaces                               | Casos de Uso                                                                  | Vistas SQL Usadas                                                                      | Tests                   |
| ---------- | ----------------------------------------------------------------------------- | ---------------------------------------- | ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | ----------------------- |
| **US-101** | —                                                                             | —                                        | —                                                                             | v_partidos_resumen, v_boxscore_completo, v_jugador_totales_temporada, v_listas_detalle | schema, FK, CHECK, seed |
| **US-102** | —                                                                             | UserRepo, ClubRepo, PlayerRepo, GameRepo | —                                                                             | (todas, vía repositorios)                                                              | integration por repo    |
| **US-103** | Usuario, Club, Jugador, JugadorClub, Competencia, Partido, EstadisticaJugador | —                                        | —                                                                             | —                                                                                      | unit entities           |
| **US-104** | —                                                                             | —                                        | RegistrarJugador, CrearClub, VincularJugador, CrearCompetencia, InscribirClub | —                                                                                      | unit con mocks          |
| **US-105** | —                                                                             | —                                        | CargarPartido                                                                 | v_partidos_resumen                                                                     | unit transacción        |
| **US-106** | —                                                                             | —                                        | RegistrarEntrenador, LoginLocal                                               | —                                                                                      | unit auth               |
| **US-107** | —                                                                             | —                                        | (reutiliza todos los UC)                                                      | v_partidos_resumen, v_boxscore_completo                                                | integration CLI         |
| **US-201** | —                                                                             | —                                        | CalcularEstadisticas                                                          | v_boxscore_completo, v_jugador_totales_temporada                                       | unit formulas (100%)    |
| **US-202** | —                                                                             | —                                        | ImportarExcel                                                                 | —                                                                                      | unit parser, unit merge |
| **US-301** | —                                                                             | —                                        | —                                                                             | v_jugador_totales_temporada, v_boxscore_completo                                       | —                       |
| **US-302** | —                                                                             | —                                        | ExportarReporte                                                               | v_boxscore_completo, v_jugador_totales_temporada                                       | unit export             |

---

## Definición de "Hecho" Técnico (DoD) — v2

Una Historia de Usuario se considera **Hecha** cuando cumple TODOS los siguientes puntos:

1. **Código integrado:** Merge a la rama principal sin conflictos; commits con formato `tipo(alcance): descripción`.

2. **Tests pasan:** Cobertura ≥ 80% en lógica de negocio. Los tests de fórmulas estadísticas requieren 100%. Todos los tests corren sin errores en CI.

3. **Arquitectura respetada:** Ninguna clase en `domain/` importa de `infrastructure/` o de librerías externas (`sqlite3`, `pandas`). Verificable con `grep` o con una herramienta de análisis de imports.

4. **SQL verificado:** Si la US crea o modifica una vista SQL, la vista está en `views.sql` y existe un test de integración que consulta la vista con datos del `seed.sql`.

5. **Transacciones:** Si la US persiste múltiples tablas (ej: partido + estadísticas), existe un test que verifica que un fallo parcial hace rollback completo.

6. **ADR documentado:** Si la US requirió una decisión arquitectónica (ej: elección de librería), el ADR correspondiente está aprobado y en el repositorio.

7. **Sin imports cruzados:** Verificar con una herramienta de linting de arquitectura que no hay violaciones de capas.

8. **Docstring mínimo:** Todos los métodos públicos tienen docstring con descripción de una línea. Los métodos complejos tienen descripción de parámetros.

---

## ADRs Pendientes de Resolución

Antes de comenzar cada hito, los siguientes ADRs deben resolverse (del PRD):

| ADR     | Título                     | Bloquea | Decisión recomendada                                                                            |
| ------- | -------------------------- | ------- | ----------------------------------------------------------------------------------------------- |
| ADR-001 | Arquitectura Local-First   | Hito 1  | ✅ SQLite + offline-first (ya definido en arquitectura.md)                                      |
| ADR-002 | Framework UI               | Hito 2  | Evaluar: Flet (Python puro, mismo stack) vs Compose Multiplatform (Java/Kotlin, mejor en móvil) |
| ADR-003 | Protocolo de Ingesta Excel | US-202  | Pandas + investigación previa de columnas reales de Ges Deportivo                               |
| ADR-004 | Versionado de DB           | Hito 2  | Evaluar: migraciones manuales con tabla `schema_version` vs `alembic`                           |
| ADR-005 | Reportes PDF               | US-302  | `reportlab` (sin dependencias externas) o `weasyprint` (HTML→PDF, más flexible)                 |
| ADR-006 | Seguridad y Cifrado        | US-106  | v0.1: SHA-256 con salt fijo. v1.0: migrar a `bcrypt` con salt dinámico                          |
| ADR-007 | Motor de Visualización     | US-301  | `matplotlib` (offline, sin servidor) o `plotly` (interactivo, requiere servidor local)          |
| ADR-008 | Estrategia de Backup       | Hito 3  | Export manual de `.db` + script de restauración                                                 |
