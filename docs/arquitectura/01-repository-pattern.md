# Guía de Estudio: Patrón Repositorio en StatsPro Basketball

> **Audiencia:** Desarrolladores del equipo incorporándose al proyecto.
> **Objetivo:** Entender el *por qué* del patrón, leer código existente con fluidez y agregar un repositorio nuevo sin romper nada.

---

## 1. Fundamentos Teóricos

### ¿Qué es el Patrón Repositorio?

Un **repositorio** es un mediador. Se ubica entre la lógica de negocio (dominio) y el sistema de persistencia (base de datos), y su única responsabilidad es la de **traducir** en ambas direcciones:

```
Base de datos (filas SQL)  ──►  Repositorio  ──►  Objetos de dominio (@dataclass)
Objetos de dominio         ──►  Repositorio  ──►  Base de datos (INSERT / UPDATE)
```

Desde el punto de vista del dominio, el repositorio parece una **colección en memoria**: simplemente pedís un jugador por ID y te lo devuelve. No importa si viene de SQLite, PostgreSQL o un archivo JSON. Eso es transparencia total.

---

### ¿Por qué se usa en Clean Architecture?

Clean Architecture organiza el código en capas concéntricas donde **las dependencias solo apuntan hacia adentro** (hacia el dominio). El patrón Repositorio es el mecanismo concreto que lo hace posible en la capa de persistencia.

| Beneficio | ¿Cómo lo resuelve el repositorio? |
|---|---|
| **Desacoplamiento** | El Dominio solo conoce la interfaz abstracta (`ABC`). Nunca importa `sqlite3`. |
| **Testabilidad** | Los tests usan la misma implementación SQLite, pero contra una DB `:memory:` efímera. |
| **Intercambiabilidad** | Reemplazar SQLite por PostgreSQL = escribir una nueva clase, sin tocar el dominio. |
| **Mapeo estricto** | Cada fila SQL se convierte en un `@dataclass` tipado; nunca circulan `dict` o `tuple` crudas. |
| **Centralización de queries** | Todas las SQL de una entidad viven en un solo archivo. Fácil de auditar. |

---

### Convención de Retornos del Proyecto

Seguimos una regla única y consistente para los tipos de retorno. **Memorizarla evita bugs silenciosos.**

| Tipo de operación | Retorno esperado | Ejemplo |
|---|---|---|
| Búsqueda individual | `Entidad \| None` | `buscar_por_id(1)` → `Jugador` o `None` |
| Búsqueda de colección | `list[Entidad]` (nunca `None`) | `obtener_todos()` → `[...]` o `[]` |
| Escritura exitosa | `Entidad` (con ID asignado) | `guardar(j)` → `Jugador(idJugador=42, ...)` |
| Escritura fallida | `None` (error de DB) | `guardar(j)` → `None` |
| Error de negocio | `raise ErrorDeDominio(...)` | `guardar(j)` → lanza `DNIDuplicadoError` |

> [!IMPORTANT]
> Las consultas de colección **siempre** retornan `list`. Nunca `None`. Esto protege al código consumidor que itera el resultado: un `for jugador in repo.buscar_por_club(99):` nunca lanzará `TypeError` aunque el club no tenga jugadores.

> [!WARNING]
> Los errores de **reglas de negocio** (ej. DNI duplicado) se lanzan como excepciones de dominio, **no** se silencian con `return None`. `None` está reservado exclusivamente para errores técnicos de la base de datos.

---

## 2. Anatomía de un Repositorio en el Proyecto

### Mapa de Capas

```
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE APLICACIÓN                       │
│              (Casos de Uso / Servicios)                     │
│                                                             │
│   caso_de_uso = RegistrarEntrenador(entrenador_repo)        │
│   entrenador_repo.guardar(entrenador)                       │
└───────────────────────┬─────────────────────────────────────┘
                        │  depende de (inyección)
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE DOMINIO                          │
│          src/dominio/repositorios/entrenador_repositorio.py │
│                                                             │
│   class EntrenadorRepositorio(ABC):        ◄── CONTRATO     │
│       @abstractmethod                                       │
│       def guardar(self, e: Entrenador) -> Entrenador | None │
│       @abstractmethod                                       │
│       def buscar_por_id(self, id: int) -> Entrenador | None │
└───────────────────────┬─────────────────────────────────────┘
                        │  implementa
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                 CAPA DE INFRAESTRUCTURA                     │
│    src/infraestructura/repositorios/                        │
│    sqlite_entrenador_repositorio.py                         │
│                                                             │
│   class SqliteEntrenadorRepositorio(EntrenadorRepositorio): │
│       def __init__(self, conexion: sqlite3.Connection)      │
│       def _row_to_entity(self, row) -> Entrenador           │
│       def guardar(self, e: Entrenador) -> Entrenador | None │
│       def buscar_por_id(self, id: int) -> Entrenador | None │
└─────────────────────────────────────────────────────────────┘
```

### Estructura de archivos del proyecto

```
src/
├── dominio/
│   ├── entidades/
│   │   ├── jugador.py          # @dataclass Jugador, JugadorClub
│   │   ├── club.py             # @dataclass Club, UsuarioClub
│   │   └── partido.py          # @dataclass Partido, JugadorPartido
│   ├── repositorios/
│   │   ├── jugador_repositorio.py      # ABC – interfaz pura
│   │   ├── club_repositorio.py         # ABC – interfaz pura
│   │   └── partido_repositorio.py      # ABC – interfaz pura
│   └── exceptions.py           # ErrorDeDominio, DNIDuplicadoError
│
└── infraestructura/
    ├── logger.py               # get_logger(__name__)
    └── repositorios/
        ├── sqlite_jugador_repositorio.py   # Implementación concreta
        ├── sqlite_club_repositorio.py      # Implementación concreta
        └── sqlite_partido_repositorio.py   # Implementación concreta

tests/
└── integration/
    ├── conftest.py                         # Fixture db_conexion (:memory:)
    ├── test_repositorios_jugador.py
    ├── test_repositorios_club.py
    └── test_repositorios_partido.py
```

---

## 3. Tutorial Paso a Paso: Agregar el Repositorio `Entrenador`

Vamos a agregar soporte completo para una entidad nueva: **`Entrenador`**. Un entrenador tiene nombre, apellido, matrícula profesional y pertenece a un club.

> [!NOTE]
> Este ejemplo es intencional y guiado. El código aquí mostrado sigue exactamente las mismas convenciones que `Jugador`, `Club` y `Partido` ya presentes en el proyecto. Leé el código real en paralelo.

---

### Paso 1 — La Entidad: `src/dominio/entidades/entrenador.py`

La entidad es un **`@dataclass` puro de Python**. No importa nada de SQLite, no tiene lógica de persistencia. Solo representa los datos y valida sus tipos en `__post_init__`.

**Reglas obligatorias:**
- El ID (`idEntrenador`) es siempre el **último atributo** y tiene valor por defecto `None` (es `None` antes de ser persistido, y un `int` positivo después).
- `__post_init__` valida **todos** los campos con `isinstance`. Nada de lanzar `ValueError` por ahora — usamos `TypeError` para señalar contratos de tipo incorrectos.
- Los campos opcionales en la DB (pueden ser `NULL`) se tipan como `tipo | None`.

```python
# src/dominio/entidades/entrenador.py

from dataclasses import dataclass


@dataclass
class Entrenador:
    nombre: str
    apellido: str
    matricula: int           # Número de matrícula profesional — debe ser único en la DB
    idClub: int              # FK al club al que pertenece
    idEntrenador: int | None = None  # None = todavía no persistido; int = ya en la DB

    def __post_init__(self):
        # Validamos cada campo. Si alguien pasa un tipo incorrecto, falla rápido y claro.
        if not isinstance(self.nombre, str):
            raise TypeError(f"nombre debe ser str, recibido {type(self.nombre).__name__}")
        if not isinstance(self.apellido, str):
            raise TypeError(f"apellido debe ser str, recibido {type(self.apellido).__name__}")
        if not isinstance(self.matricula, int):
            raise TypeError(f"matricula debe ser int, recibido {type(self.matricula).__name__}")
        if not isinstance(self.idClub, int):
            raise TypeError(f"idClub debe ser int, recibido {type(self.idClub).__name__}")
        # El ID puede ser None (antes de guardar) o int (después de guardar)
        if self.idEntrenador is not None and not isinstance(self.idEntrenador, int):
            raise TypeError(
                f"idEntrenador debe ser int o None, recibido {type(self.idEntrenador).__name__}"
            )
```

**¿Por qué el ID es el último atributo con default `None`?**

Los `@dataclass` en Python no permiten que un campo con valor por defecto aparezca *antes* de uno sin valor por defecto. Como el ID es el único con `None`, siempre va al final. Además, al construir la entidad *antes* de guardarla, simplemente no pasás el ID:

```python
# Antes de guardar: idEntrenador es None implícitamente
nuevo = Entrenador(nombre="Rubén", apellido="Magnano", matricula=4501, idClub=1)
print(nuevo.idEntrenador)  # → None

# Después de guardar: el repositorio reconstruye el objeto con el ID asignado por la DB
guardado = repo.guardar(nuevo)
print(guardado.idEntrenador)  # → 7 (o cualquier AUTOINCREMENT que asignó SQLite)
```

---

### Paso 2 — El Contrato: `src/dominio/repositorios/entrenador_repositorio.py`

El contrato es una **clase abstracta** que define *qué* puede hacerse, sin decir *cómo*. Hereda de `ABC` y decora cada método con `@abstractmethod`.

**Reglas obligatorias:**
- Solo importa del dominio: `from dominio.entidades.entrenador import Entrenador`. Cero imports de `sqlite3`.
- Cada método tiene un docstring de una línea que explica su intención.
- Los tipos de retorno deben respetar la convención de la sección 1.

```python
# src/dominio/repositorios/entrenador_repositorio.py

from abc import ABC, abstractmethod

from dominio.entidades.entrenador import Entrenador


class EntrenadorRepositorio(ABC):
    """Define el contrato de persistencia para la entidad Entrenador."""

    @abstractmethod
    def guardar(self, entrenador: Entrenador) -> Entrenador | None:
        """Persiste un Entrenador nuevo. Retorna la entidad con ID asignado, o None si hay error de DB."""
        pass

    @abstractmethod
    def buscar_por_id(self, id_entrenador: int) -> Entrenador | None:
        """Retorna el Entrenador con ese ID, o None si no existe."""
        pass

    @abstractmethod
    def buscar_por_matricula(self, matricula: int) -> Entrenador | None:
        """Retorna el Entrenador con esa matrícula, o None si no existe."""
        pass

    @abstractmethod
    def obtener_por_club(self, id_club: int) -> list[Entrenador]:
        """Retorna todos los entrenadores del club. Lista vacía si no hay ninguno."""
        pass
```

> [!TIP]
> Notá la diferencia de retorno entre `buscar_por_id` (`Entrenador | None`) y `obtener_por_club` (`list[Entrenador]`). La primera es una búsqueda individual que puede no encontrar nada. La segunda es una colección: aunque esté vacía, es una lista válida y operable.

---

### Paso 3 — La Implementación: `src/infraestructura/repositorios/sqlite_entrenador_repositorio.py`

Esta clase concreta es la única que sabe qué es SQLite. Acá viven todas las queries SQL.

**Estructura interna de la clase:**

```
SqliteEntrenadorRepositorio
│
├── __init__(conexion)         ← Inyección de dependencia
├── _row_to_entity(row)        ← Método privado de mapeo (Row → @dataclass)
├── guardar(entrenador)        ← Escritura con manejo de transacción
├── buscar_por_id(id)          ← Lectura individual
├── buscar_por_matricula(m)    ← Lectura individual
└── obtener_por_club(id_club)  ← Lectura de colección
```

```python
# src/infraestructura/repositorios/sqlite_entrenador_repositorio.py

import sqlite3

from dominio.entidades.entrenador import Entrenador
from dominio.exceptions import ErrorDeDominio          # Base de excepciones de negocio
from dominio.repositorios.entrenador_repositorio import EntrenadorRepositorio
from infraestructura.logger import get_logger

# El logger usa el nombre del módulo para identificar el origen en los logs.
# Ejemplo de salida: "2026-08-16 - infraestructura.repositorios.sqlite_entrenador_repositorio - ERROR - ..."
logger = get_logger(__name__)


class SqliteEntrenadorRepositorio(EntrenadorRepositorio):

    def __init__(self, conexion: sqlite3.Connection):
        # Inyección de dependencia: recibimos la conexión desde afuera.
        # Esto permite que los tests pasen una conexión :memory: sin modificar esta clase.
        self.conexion = conexion

    # ──────────────────────────────────────────────────
    # MÉTODO PRIVADO DE MAPEO
    # ──────────────────────────────────────────────────

    def _row_to_entity(self, row: sqlite3.Row) -> Entrenador:
        """Convierte una fila de SQLite (sqlite3.Row) en una instancia de Entrenador.

        sqlite3.Row permite acceso por nombre de columna (row["idEntrenador"]) en lugar
        de por índice (row[0]), lo que hace el código robusto ante cambios de orden en la SELECT.
        Esto funciona siempre que la conexión tenga configurado `conexion.row_factory = sqlite3.Row`,
        lo cual está garantizado en el fixture de tests y en el DatabaseManager.
        """
        return Entrenador(
            nombre=row["nombre"],
            apellido=row["apellido"],
            matricula=row["matricula"],
            idClub=row["idClub"],
            idEntrenador=row["idEntrenador"],
        )

    # ──────────────────────────────────────────────────
    # ESCRITURA
    # ──────────────────────────────────────────────────

    def guardar(self, entrenador: Entrenador) -> Entrenador | None:
        cursor = self.conexion.cursor()
        try:
            query = """
            INSERT INTO entrenador (nombre, apellido, matricula, idClub)
            VALUES (?, ?, ?, ?);
            """
            cursor.execute(
                query,
                (entrenador.nombre, entrenador.apellido, entrenador.matricula, entrenador.idClub),
            )
            self.conexion.commit()
            # lastrowid devuelve el AUTOINCREMENT asignado por SQLite al INSERT anterior.
            # Es el mecanismo estándar para obtener el ID recién generado.
            id_entrenador = cursor.lastrowid

        except sqlite3.Error as e:
            # Capturamos errores técnicos de la DB (tabla no existe, FK violada, etc.)
            # y los transformamos en un retorno None sin propagar la excepción de SQLite
            # hacia el dominio, que no debería conocer sqlite3.Error.
            logger.error(f"Error al guardar Entrenador: {e}", exc_info=True)
            return None

        # Construimos y retornamos la entidad con el ID recién asignado.
        # Lo hacemos FUERA del try/except de sqlite3 para que un TypeError en la
        # construcción del @dataclass propague hacia arriba (es un bug del programador,
        # no un error esperado de la DB).
        try:
            return Entrenador(
                nombre=entrenador.nombre,
                apellido=entrenador.apellido,
                matricula=entrenador.matricula,
                idClub=entrenador.idClub,
                idEntrenador=id_entrenador,
            )
        except TypeError as e:
            # Esto solo puede pasar si el schema de la DB retorna un tipo inesperado.
            # Es un error crítico de programación, no de uso normal.
            logger.critical(
                f"Entrenador guardado (id={id_entrenador}) pero no se pudo reconstruir el objeto: {e}"
            )
            raise  # Re-lanzamos: no silenciamos bugs estructurales.

    # ──────────────────────────────────────────────────
    # LECTURAS INDIVIDUALES
    # ──────────────────────────────────────────────────

    def buscar_por_id(self, id_entrenador: int) -> Entrenador | None:
        cursor = self.conexion.cursor()
        query = "SELECT * FROM entrenador WHERE idEntrenador = ?;"
        cursor.execute(query, (id_entrenador,))  # ← La coma crea una tupla. Sin ella es un error.
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_entity(row)

    def buscar_por_matricula(self, matricula: int) -> Entrenador | None:
        cursor = self.conexion.cursor()
        query = "SELECT * FROM entrenador WHERE matricula = ?;"
        cursor.execute(query, (matricula,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_entity(row)

    # ──────────────────────────────────────────────────
    # LECTURA DE COLECCIÓN
    # ──────────────────────────────────────────────────

    def obtener_por_club(self, id_club: int) -> list[Entrenador]:
        cursor = self.conexion.cursor()
        query = "SELECT * FROM entrenador WHERE idClub = ?;"
        cursor.execute(query, (id_club,))
        rows = cursor.fetchall()
        # fetchall() retorna [] si no hay resultados; nunca None.
        # Pero igualmente lo guardamos como convención explícita.
        if not rows:
            return []
        return [self._row_to_entity(row) for row in rows]
```

#### Anatomía del try/except en `guardar`

Este es el patrón de manejo de errores que usamos en **todo** el proyecto. Es importante entenderlo bien:

```
try:
    [ejecutar INSERT + commit]
except sqlite3.IntegrityError as e:       ← Error de reglas de la DB (UNIQUE, FK, CHECK)
    if es_error_de_negocio(e):
        raise ErrorDeDominio(...) from e  ← Se propaga como excepción de dominio
    return None                           ← Otros errores de integridad → silenciar
except sqlite3.Error as e:               ← Cualquier otro error técnico de SQLite
    logger.error(...)
    return None                           ← Silenciar: el llamador recibe None
```

> [!NOTE]
> `sqlite3.IntegrityError` es subclase de `sqlite3.Error`. Por eso el `except IntegrityError` **debe ir primero**: Python evalúa los `except` en orden y el más específico debe ir antes del más general.

---

### Paso 4 — Tests de Integración: `tests/integration/test_repositorios_entrenador.py`

Los tests usan la fixture `db_conexion` definida en `tests/conftest.py`. Esa fixture crea una base de datos SQLite **en memoria** (`:memory:`), ejecuta el `schema.sql` y el `seed.sql`, y la destruye al terminar cada test. Cada test parte de un estado limpio y predecible.

```python
# tests/integration/test_repositorios_entrenador.py

import pytest

from dominio.entidades.entrenador import Entrenador
from infraestructura.repositorios.sqlite_entrenador_repositorio import SqliteEntrenadorRepositorio


# ─────────────────────────────────────────────────────────────────
# TESTS DE ESCRITURA
# ─────────────────────────────────────────────────────────────────

def test_guardar_asigna_id(db_conexion):
    """Un entrenador nuevo debe quedar persistido y recibir un ID autoincremental."""
    repo = SqliteEntrenadorRepositorio(db_conexion)

    nuevo = Entrenador(nombre="Rubén", apellido="Magnano", matricula=4501, idClub=1)
    assert nuevo.idEntrenador is None  # Antes de guardar: sin ID

    guardado = repo.guardar(nuevo)

    assert guardado is not None
    assert guardado.idEntrenador is not None          # Después de guardar: tiene ID
    assert isinstance(guardado.idEntrenador, int)     # Y es un entero positivo
    assert guardado.idEntrenador > 0
    assert guardado.nombre == "Rubén"
    assert guardado.matricula == 4501


def test_guardar_retorna_none_si_club_no_existe(db_conexion):
    """Si el club referenciado no existe, la FK falla y guardar retorna None."""
    repo = SqliteEntrenadorRepositorio(db_conexion)
    # idClub=99999 no existe en el seed → violación de FK → None
    e = Entrenador(nombre="Test", apellido="Falla", matricula=9999, idClub=99999)
    resultado = repo.guardar(e)
    assert resultado is None


# ─────────────────────────────────────────────────────────────────
# TESTS DE LECTURA INDIVIDUAL
# ─────────────────────────────────────────────────────────────────

def test_buscar_por_id_existente(db_conexion):
    """Guardar y luego buscar por ID debe devolver la misma entidad."""
    repo = SqliteEntrenadorRepositorio(db_conexion)
    guardado = repo.guardar(
        Entrenador(nombre="Pablo", apellido="Prigioni", matricula=1101, idClub=1)
    )

    encontrado = repo.buscar_por_id(guardado.idEntrenador)

    assert encontrado is not None
    assert encontrado.idEntrenador == guardado.idEntrenador
    assert encontrado.nombre == "Pablo"
    assert encontrado.matricula == 1101


def test_buscar_por_id_inexistente_retorna_none(db_conexion):
    """Buscar un ID que no existe debe retornar None, no lanzar excepción."""
    repo = SqliteEntrenadorRepositorio(db_conexion)
    resultado = repo.buscar_por_id(99999)
    assert resultado is None


def test_buscar_por_matricula_existente(db_conexion):
    """Buscar por matrícula debe funcionar igual que buscar por ID."""
    repo = SqliteEntrenadorRepositorio(db_conexion)
    repo.guardar(Entrenador(nombre="Néstor", apellido="García", matricula=7777, idClub=1))

    encontrado = repo.buscar_por_matricula(7777)
    assert encontrado is not None
    assert encontrado.apellido == "García"


# ─────────────────────────────────────────────────────────────────
# TESTS DE COLECCIÓN
# ─────────────────────────────────────────────────────────────────

def test_obtener_por_club_retorna_lista(db_conexion):
    """Con entrenadores cargados, obtener_por_club devuelve lista no vacía."""
    repo = SqliteEntrenadorRepositorio(db_conexion)
    repo.guardar(Entrenador(nombre="A", apellido="B", matricula=1001, idClub=1))
    repo.guardar(Entrenador(nombre="C", apellido="D", matricula=1002, idClub=1))

    resultado = repo.obtener_por_club(1)

    assert isinstance(resultado, list)  # Siempre es una lista...
    assert len(resultado) >= 2          # ...con al menos los 2 que acabamos de guardar
    assert all(isinstance(e, Entrenador) for e in resultado)  # ...de tipo correcto


def test_obtener_por_club_sin_entrenadores_retorna_lista_vacia(db_conexion):
    """Si el club no tiene entrenadores, el resultado debe ser [] y NO None."""
    repo = SqliteEntrenadorRepositorio(db_conexion)

    resultado = repo.obtener_por_club(99999)  # Club inexistente

    assert resultado == []                # Lista vacía: válida e iterable
    assert isinstance(resultado, list)    # Explícitamente verificamos que es lista
    # Esto garantiza que un "for e in resultado" nunca lanzará TypeError
```

#### Por qué probamos `[]` explícitamente

```python
# ✅ Correcto — con lista vacía, el bucle simplemente no itera
entrenadores = repo.obtener_por_club(99)  # → []
for e in entrenadores:
    print(e.nombre)  # Nunca ejecuta, pero tampoco lanza error

# ❌ Peligroso — con None, el bucle explota
entrenadores = repo.obtener_por_club(99)  # → None (si hubiéramos retornado None)
for e in entrenadores:                     # TypeError: 'NoneType' object is not iterable
    print(e.nombre)
```

---

## 4. Checklist de Pull Request

Antes de abrir un PR con un repositorio nuevo, verificá que **todos** los ítems estén cumplidos:

### Entidad (`src/dominio/entidades/`)

- [ ] Es un `@dataclass` puro. No importa `sqlite3` ni ningún framework.
- [ ] El ID es el último atributo y tiene valor por defecto `None`.
- [ ] `__post_init__` valida el tipo de **todos** los campos con `isinstance`.
- [ ] Los campos opcionales en la DB están tipados como `tipo | None`.

### Interfaz Abstracta (`src/dominio/repositorios/`)

- [ ] Hereda de `ABC` y está en el módulo `dominio`.
- [ ] Solo importa entidades del dominio. Cero imports de `infraestructura` o `sqlite3`.
- [ ] Todos los métodos tienen `@abstractmethod` y type hints completos en firma.
- [ ] Las colecciones retornan `list[Entidad]`, **nunca** `list[Entidad] | None`.
- [ ] Cada método tiene un docstring de una línea.

### Implementación SQLite (`src/infraestructura/repositorios/`)

- [ ] El nombre sigue la convención `sqlite_<nombre>_repositorio.py`.
- [ ] Hereda de la interfaz abstracta del dominio.
- [ ] Recibe `sqlite3.Connection` por constructor (inyección de dependencia).
- [ ] Tiene `_row_to_entity(self, row: sqlite3.Row) -> Entidad` como método privado.
- [ ] Los `except` son `except sqlite3.Error as e:` — nunca `except sqlite3.Error:` (sin `as e`).
- [ ] Los mensajes de log mencionan la entidad correcta (no copiar/pegar mensajes de otro repo).
- [ ] Las consultas de colección retornan `[]` ante ausencia de resultados, **nunca** `None`.
- [ ] Los errores de reglas de negocio lanzan excepciones de `dominio.exceptions`, no retornan `None`.
- [ ] El segundo `try/except TypeError` existe para detectar bugs de construcción y hace `raise`.

### Schema SQL (`src/infraestructura/persistencia/sql/schema.sql`)

- [ ] La tabla nueva está en `schema.sql` con `CREATE TABLE IF NOT EXISTS`.
- [ ] El ID usa `INTEGER PRIMARY KEY AUTOINCREMENT`.
- [ ] Las FKs tienen `ON DELETE CASCADE ON UPDATE CASCADE` según corresponda.
- [ ] La tabla usa la cláusula `STRICT` para reforzar tipos en SQLite.
- [ ] Los `DROP TABLE IF EXISTS` están al inicio del script en orden correcto (FK primero).

### Tests (`tests/integration/`)

- [ ] El archivo se llama `test_repositorios_<nombre>.py`.
- [ ] Usa la fixture `db_conexion` (o `db_conexion_sin_seed` si aplica).
- [ ] Hay test de `guardar` que verifica que el ID resultante **no es None** y es `int`.
- [ ] Hay test de `buscar_por_id` con ID existente (retorna entidad correcta).
- [ ] Hay test de `buscar_por_id` con ID inexistente (retorna `None`).
- [ ] Hay test de colección que verifica retorno de `list` con elementos.
- [ ] Hay test de colección vacía que verifica retorno de `[]` (no `None`).
- [ ] Si hay excepciones de dominio, hay un test con `pytest.raises(ErrorDeDominio)`.
- [ ] `ruff check` pasa sin errores nuevos.
- [ ] `pytest` pasa en verde con los tests nuevos incluidos.

---

## Referencia Rápida: Comparativa de Métodos

| Método | Retorno | `fetchone` / `fetchall` | ¿Puede retornar `None`? |
|---|---|---|---|
| `guardar(entidad)` | `Entidad \| None` | `cursor.lastrowid` | Sí (error de DB) |
| `buscar_por_id(id)` | `Entidad \| None` | `fetchone()` | Sí (no encontrado) |
| `buscar_por_X(x)` | `Entidad \| None` | `fetchone()` | Sí (no encontrado) |
| `obtener_todos()` | `list[Entidad]` | `fetchall()` | **No** — mínimo `[]` |
| `obtener_por_X(x)` | `list[Entidad]` | `fetchall()` | **No** — mínimo `[]` |

---

## Preguntas Frecuentes

**¿Por qué no usamos un ORM como SQLAlchemy?**
El proyecto elige SQL explícito para que cada integrante entienda exactamente qué consultas se ejecutan, sin magia de fondo. Los repositorios son livianísimos y suficientes para el dominio actual.

**¿Por qué `row_factory = sqlite3.Row` en la conexión?**
Sin eso, las filas son tuplas (`row[0]`, `row[1]`...). Con `sqlite3.Row`, son accesibles por nombre (`row["nombre"]`), lo que hace el código legible y resistente a cambios de orden en las columnas de la SELECT.

**¿Dónde pongo la lógica de negocio compleja que necesita múltiples repositorios?**
En un **Caso de Uso** (Servicio de Aplicación), nunca en el repositorio. El repositorio solo persiste y recupera. La orquestación le corresponde a la capa de aplicación, que recibe ambos repositorios por inyección de dependencia.

**¿Qué pasa si necesito una operación atómica que afecta dos tablas?**
Usamos el context manager de sqlite3: `with self.conexion:`. Cualquier excepción dentro del bloque hace ROLLBACK automático; si sale sin error, hace COMMIT. Ver `save_with_boxscore` en `sqlite_partido_repositorio.py` como ejemplo real del proyecto.
