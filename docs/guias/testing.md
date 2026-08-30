# Guía: Testing — conceptos, técnicas y ejemplos aplicados al proyecto

> Guía de referencia, pensada para consultarse cada vez que arranquen un test nuevo — no hace
> falta leerla entera de una sentada. Todos los ejemplos usan clases y dataclasses reales del
> proyecto (`Jugador`, `JugadorRepositorio`, `RegistrarJugadorUseCase`), no ejemplos genéricos.

## 0. Lo que ya tienen andando (punto de partida)

Antes de sumar nada nuevo, esto es lo que ya existe y funciona en el proyecto:

- `pytest` + `pytest-cov` como runner (ver `requerimientos.txt` y `pytest.ini`).
- `tests/integration/` con tests que golpean una base SQLite **real, en memoria** (`:memory:`),
  armada por las fixtures de `tests/conftest.py` (`db_conexion`, `db_conexion_sin_seed`,
  `db_conexion_sandbox`).
- `tests/unit/` **ya existe como carpeta, vacía** — está reservada para lo que agrega esta guía:
  tests que **no** tocan SQLite.
- `make run_test` corre `pytest -v --cov=src --cov-report=html` (reporte de cobertura en HTML).
- No hay ninguna librería de mocking de terceros instalada (no está `pytest-mock`) — toda la
  sección 3 de esta guía usa `unittest.mock`, que es parte de la librería estándar de Python, no
  hace falta instalar nada.

---

## 1. Unitario vs. integración — la diferencia real, no de nombre de carpeta

La diferencia **no** es "está en `tests/unit/` o en `tests/integration/`" — esa es solo la
convención de carpetas. La diferencia real es **qué tan real es lo que hay del otro lado**:

| | Test unitario | Test de integración |
| --- | --- | --- |
| Qué prueba | Una unidad de lógica aislada (una clase, un método) | Que dos o más piezas reales funcionan bien **juntas** |
| Dependencias externas (DB, filesystem, red) | Reemplazadas por un doble de prueba (sección 2) | Reales (o una réplica fiel, ej. SQLite `:memory:`) |
| Velocidad | Microsegundos — miles corren en segundos | Más lento — arma esquema, corre SQL real |
| Qué significa que falle | Hay un bug en la lógica de esa unidad | Hay un bug en cómo esa unidad usa SQL/el filesystem/etc, o en el propio SQL |

**Ejemplo concreto con código que ya tienen:**

- `tests/integration/test_repositorios_jugador.py::test_guardar_jugador_dni_duplicado_lanza_excepcion`
  es de **integración**: usa `db_conexion` (SQLite real en memoria) y prueba que el `INSERT`
  compite de verdad contra una fila ya sembrada por el seed. Si mañana cambia el nombre de la
  columna `dni` en `schema.sql` sin actualizar el repo, **este** test lo detecta.
- Un test nuevo para `RegistrarJugadorUseCase` (que todavía no existe) debería ser **unitario**:
  no necesita SQLite para nada — necesita solo confirmar que, dado un repositorio que dice "el DNI
  ya existe", el caso de uso lanza `DNIDuplicadoError` **antes** de intentar guardar. Eso es una
  decisión de lógica pura, no de SQL.

**Regla práctica para decidir dónde va un test nuevo:** si para escribirlo necesitás una fixture
que abra una conexión SQLite, es de integración. Si podés escribirlo pasando objetos Python
comunes (dataclasses, un objeto de prueba armado a mano), es unitario y va en `tests/unit/`.

---

## 2. Test doubles — el vocabulario de "objetos de prueba"

"Mock" es el término que todo el mundo usa como genérico, pero en realidad hay **cinco tipos**
distintos de "objeto de prueba" (test double), cada uno con un propósito distinto. Vale la pena
distinguirlos porque usar el tipo equivocado hace tests confusos o frágiles:

| Tipo | Qué hace | Ejemplo en este proyecto |
| --- | --- | --- |
| **Dummy** | Se pasa porque hace falta el parámetro, pero nunca se usa de verdad. | Un `Jugador` de relleno pasado a una función que ni lo mira. |
| **Stub** | Devuelve respuestas fijas y predefinidas a los llamados que recibe, sin lógica. | Un objeto cuyo `buscar_por_dni()` siempre devuelve `None`, sin importar el DNI. |
| **Fake** | Tiene una implementación **real pero simplificada** (funciona de verdad, pero no es la de producción). | Un `JugadorRepositorio` respaldado por un `dict` en memoria en vez de SQLite — funciona de verdad (guardás y después lo encontrás), pero no persiste a disco. |
| **Mock** | Además de responder, **registra cómo lo llamaron** para poder verificar después ("¿se llamó una vez? ¿con qué argumentos?"). | `Mock(spec=JugadorRepositorio)` de `unittest.mock`, verificado con `.assert_called_once_with(...)`. |
| **Spy** | Como un Mock, pero envuelve un objeto **real** y deja que la llamada real pase, además de registrarla. | Poco común en este proyecto — más útil cuando querés confirmar que se llamó a un servicio real sin reemplazar su comportamiento. |

**Para los casos de uso de la US-103, van a usar sobre todo dos: Fake y Mock** — la sección 3
muestra ambos con el mismo ejemplo, para que se vea la diferencia de estilo.

---

## 3. `unittest.mock` — la herramienta (sin instalar nada nuevo)

`unittest.mock` viene con Python. Las piezas que más van a usar:

### 3.1 `Mock()` y `MagicMock()`

Un `Mock` es un objeto que **acepta cualquier atributo o llamada** que le hagas, y por defecto
devuelve otro `Mock` (encadenable). No tiene comportamiento propio — hay que decirle qué
devolver.

```python
from unittest.mock import Mock

repo_falso = Mock()
repo_falso.buscar_por_dni.return_value = None   # "decile" qué devolver cuando lo llamen así

resultado = repo_falso.buscar_por_dni(12345678)
print(resultado)  # None
```

`MagicMock` es lo mismo que `Mock`, pero además soporta métodos "mágicos" de Python
(`__len__`, `__iter__`, etc.) — para los repositorios de este proyecto no hace falta, `Mock`
alcanza.

### 3.2 `spec=` — la protección contra errores de tipeo

El problema de un `Mock()` a secas es que **acepta cualquier nombre de método**, incluso uno que
no existe en la interfaz real — si le pusiste `repo_falso.buscar_por_dnii` (con una i de más) por
error de tipeo, el `Mock` lo deja pasar sin quejarse, y el test "pasa" probando algo que no es lo
que creías. La solución es `spec`:

```python
from unittest.mock import Mock
from dominio.repositorios.jugador_repositorio import JugadorRepositorio

repo_falso = Mock(spec=JugadorRepositorio)
repo_falso.buscar_por_dnii(123)   # AttributeError: no existe ese método en JugadorRepositorio
```

**Recomendación:** usen `spec=` (o `spec_set=`, más estricto todavía) siempre que mockeen algo que
tenga una interfaz real (como `JugadorRepositorio`) — es casi gratis y evita una categoría entera
de tests rotos silenciosamente.

### 3.3 `return_value` vs. `side_effect`

- `return_value`: siempre devuelve lo mismo, sin importar los argumentos.
- `side_effect`: permite devolver algo distinto según la llamada, **o lanzar una excepción** — es
  lo que usan para simular "esto falla":

```python
from dominio.exceptions import DNIDuplicadoError

repo_falso = Mock(spec=JugadorRepositorio)
repo_falso.guardar.side_effect = DNIDuplicadoError("DNI ya registrado")
```

También puede ser una función, para lógica condicional (ej. devolver distinto según el DNI
recibido):

```python
def fake_buscar_por_dni(dni):
    return Jugador(nombre="Pepe", apellido="Argento", dni=dni, anioNacimiento=1980, idJugador=1) if dni == 12351689 else None

repo_falso.buscar_por_dni.side_effect = fake_buscar_por_dni
```

### 3.4 Verificar llamadas — la parte "Mock" del Mock

```python
repo_falso.guardar.assert_called_once()               # se llamó exactamente una vez
repo_falso.guardar.assert_called_once_with(jugador)    # ... y con ese argumento exacto
repo_falso.buscar_por_dni.assert_not_called()          # nunca se llamó
```

Esto es lo que un Fake **no** te da gratis (podrías agregarlo a mano, pero no es su rol) — el
Mock es la herramienta cuando lo que te importa verificar es **la interacción** ("¿se llamó a
`guardar` con el jugador correcto?"), no solo el resultado final.

### 3.5 `patch` — reemplazar algo que se importa adentro de otro módulo

`patch` sirve para el caso en que el código bajo test **crea** su propia dependencia en vez de
recibirla por constructor (por ejemplo, si un comando CLI hiciera
`SqliteJugadorRepositorio(conexion)` adentro suyo en vez de recibir el repo ya armado). Con
Inyección de Dependencias bien aplicada (que es justo lo que pide el AC2 de la US-103, ver el
[documento de la US](../context_ia/2026-08-17-us103-explicada-en-profundidad.md#122-ac2--inyección-de-dependencias)),
**casi nunca van a necesitar `patch`** — le pasan el Fake/Mock directo por parámetro. Se
menciona acá porque es una herramienta muy nombrada y conviene saber cuándo NO hace falta:

```python
from unittest.mock import patch

with patch("infraestructura.persistencia.database_manager.SQLiteManager.connect") as mock_connect:
    mock_connect.return_value = "conexion-falsa"
    ...
```

Si se encuentran necesitando `patch` seguido, suele ser una señal de que a esa clase le falta
recibir la dependencia por constructor (repasar AC2).

---

## 4. Ejemplo completo: testeando `RegistrarJugadorUseCase`

Dos versiones del mismo test — con **Fake** primero, con **Mock** después — para que se vea la
diferencia de enfoque. Van en `tests/unit/test_registrar_jugador_use_case.py`.

### 4.1 Versión con Fake (una implementación real y simplificada)

```python
from dominio.entidades.jugador import Jugador
from dominio.exceptions import DNIDuplicadoError
from dominio.repositorios.jugador_repositorio import JugadorRepositorio
from aplicacion.casos_uso.registrar_jugador import RegistrarJugadorUseCase
from aplicacion.DTOs.jugador_dto import CrearJugadorDTO
import pytest


class JugadorRepositorioFake(JugadorRepositorio):
    """Repositorio en memoria: cumple la interfaz real, sin tocar SQLite."""

    def __init__(self):
        self._jugadores: dict[int, Jugador] = {}
        self._siguiente_id = 1

    def buscar_por_id(self, id_jugador):
        return self._jugadores.get(id_jugador)

    def buscar_por_dni(self, dni_jugador):
        return next((j for j in self._jugadores.values() if j.dni == dni_jugador), None)

    def buscar_por_club(self, idClub):
        return []

    def guardar(self, jugador):
        if self.buscar_por_dni(jugador.dni) is not None:
            raise DNIDuplicadoError(f"Ya existe un jugador con DNI {jugador.dni}")
        guardado = Jugador(
            nombre=jugador.nombre,
            apellido=jugador.apellido,
            dni=jugador.dni,
            anioNacimiento=jugador.anioNacimiento,
            idJugador=self._siguiente_id,
        )
        self._jugadores[self._siguiente_id] = guardado
        self._siguiente_id += 1
        return guardado

    def link_to_club(self, jc):
        raise NotImplementedError

    def club_activo(self, id_jugador):
        raise NotImplementedError


def test_registrar_jugador_camino_feliz():
    repo = JugadorRepositorioFake()
    caso_uso = RegistrarJugadorUseCase(jugador_repo=repo)
    dto = CrearJugadorDTO(nombre="Lionel", apellido="Messi", dni=33016244, anioNacimiento=1987)

    resultado = caso_uso.ejecutar(dto)

    assert resultado.idJugador == 1
    assert resultado.nombre == "Lionel"


def test_registrar_jugador_dni_duplicado_lanza_excepcion():
    repo = JugadorRepositorioFake()
    caso_uso = RegistrarJugadorUseCase(jugador_repo=repo)
    dto = CrearJugadorDTO(nombre="Lionel", apellido="Messi", dni=33016244, anioNacimiento=1987)
    caso_uso.ejecutar(dto)  # primer registro, ocupa el DNI

    with pytest.raises(DNIDuplicadoError):
        caso_uso.ejecutar(dto)  # segundo intento, mismo DNI
```

Nota: hay que implementar todos los métodos abstractos de `JugadorRepositorio` (como
`link_to_club`, `club_activo`) aunque este test no los use — es el costo de que el Fake respete
la interfaz completa. Si eso empieza a molestar en muchos tests, es una señal para revisar si
`JugadorRepositorio` no está haciendo demasiadas cosas a la vez (ver Interface Segregation, fuera
del alcance de esta guía).

### 4.2 La misma prueba con Mock (verificando la interacción, no la lógica interna)

```python
from unittest.mock import Mock
import pytest

from dominio.entidades.jugador import Jugador
from dominio.exceptions import DNIDuplicadoError
from dominio.repositorios.jugador_repositorio import JugadorRepositorio
from aplicacion.casos_uso.registrar_jugador import RegistrarJugadorUseCase
from aplicacion.DTOs.jugador_dto import CrearJugadorDTO


def test_registrar_jugador_llama_guardar_con_el_jugador_correcto():
    repo_mock = Mock(spec=JugadorRepositorio)
    repo_mock.guardar.return_value = Jugador(
        nombre="Lionel", apellido="Messi", dni=33016244, anioNacimiento=1987, idJugador=1
    )
    caso_uso = RegistrarJugadorUseCase(jugador_repo=repo_mock)
    dto = CrearJugadorDTO(nombre="Lionel", apellido="Messi", dni=33016244, anioNacimiento=1987)

    resultado = caso_uso.ejecutar(dto)

    # No nos importa cómo el repo "guarda" — nos importa que el caso de uso
    # haya construido bien el Jugador y se lo haya pasado a guardar().
    repo_mock.guardar.assert_called_once()
    jugador_pasado = repo_mock.guardar.call_args[1]["jugador"]
    assert jugador_pasado.dni == 33016244
    assert resultado.idJugador == 1


def test_registrar_jugador_propaga_dni_duplicado(monkeypatch):
    repo_mock = Mock(spec=JugadorRepositorio)
    repo_mock.guardar.side_effect = DNIDuplicadoError("Ya existe un jugador con DNI 33016244")
    caso_uso = RegistrarJugadorUseCase(jugador_repo=repo_mock)
    dto = CrearJugadorDTO(nombre="Lionel", apellido="Messi", dni=33016244, anioNacimiento=1987)

    with pytest.raises(DNIDuplicadoError):
        caso_uso.ejecutar(dto)
```

**¿Cuándo usar cada uno?** Fake cuando la prueba necesita que el repositorio "se comporte bien"
de verdad a través de varias llamadas (guardar y después poder buscar lo guardado, como en
`test_registrar_jugador_dni_duplicado_lanza_excepcion` de arriba). Mock cuando lo único que
importa es **qué le pasaron a un método puntual** y no hace falta que ese método tenga lógica de
verdad detrás (`test_registrar_jugador_llama_guardar_con_el_jugador_correcto`). Para casos de uso
simples, el Fake suele ganar en legibilidad; para verificar interacciones puntuales sin escribir
una clase entera, el Mock es más rápido de armar.

---

## 5. Testeando comandos CLI (`jugador_add.ejecutar`, etc.)

Esta es la parte nueva a nivel de técnica que trae la US-103. Dos herramientas de `pytest` que
todavía no usaron:

### 5.1 Armar un `Namespace` a mano — sin pasar por `sys.argv`

No hace falta simular una terminal real. `argparse.Namespace` es solo un objeto con atributos —
se puede instanciar directo:

```python
import argparse
from infraestructura.ui.cli.commands import jugador_add

args = argparse.Namespace(nombre="Lionel", apellido="Messi", dni=33016244, anio=1987)
jugador_add.ejecutar(args)
```

Alternativa, si quieren probar también que el parser arma bien esos argumentos (útil para un test
de "contrato" del propio parser, separado del test del handler):

```python
parser = construir_parser()
args = parser.parse_args(["jugador", "add", "--nombre", "Lionel", "--apellido", "Messi", "--dni", "33016244", "--anio", "1987"])
assert args.nombre == "Lionel"
assert args.func is jugador_add.ejecutar
```

Pasarle una `list[str]` a `parse_args()` (en vez de omitir el argumento) hace que lea esa lista en
vez de `sys.argv` — así el test no depende de cómo se ejecutó `pytest`.

### 5.2 `capsys` — capturar lo que el comando imprime

`capsys` es una fixture nativa de `pytest` (no requiere nada extra) que captura todo lo que pasó
por `print()` durante el test:

```python
from infraestructura.ui.cli.commands import jugador_add


def test_jugador_add_ejecutar_imprime_confirmacion(capsys):
    args = argparse.Namespace(nombre="Lionel", apellido="Messi", dni=33016244, anio=1987)
    repo_fake = JugadorRepositorioFake()

    jugador_add.ejecutar(args, repo=repo_fake)   # ver nota abajo sobre inyectar el repo

    salida = capsys.readouterr().out
    assert "Lionel Messi" in salida
    assert "id=1" in salida


def test_jugador_add_ejecutar_muestra_error_amigable_sin_traceback(capsys):
    args = argparse.Namespace(nombre="Lionel", apellido="Messi", dni=33016244, anio=1987)
    repo_fake = JugadorRepositorioFake()
    repo_fake.guardar(Jugador(nombre="Otro", apellido="Jugador", dni=33016244, anioNacimiento=1990))

    jugador_add.ejecutar(args, repo=repo_fake)   # mismo DNI, ya ocupado

    salida = capsys.readouterr().out
    assert "Error" in salida
    assert "Traceback" not in salida   # confirma el AC3: fail-fast sin traceback crudo
```

**Nota importante de diseño para que esto sea testeable:** si `jugador_add.ejecutar(args)` arma la
conexión SQLite real *adentro suyo sin parámetro para reemplazarla*, no hay forma de pasarle un
repo Fake — quedaría forzado a tocar SQLite real en cada test del comando. La solución es la que
ya usa (ver [el documento de flujo completo, sección 5](../context_ia/2026-08-29-us103-argparse-comandos-flujo-completo.md#5-la-función-ejecutar-de-un-comando--de-dónde-salen-sus-dependencias)):
el comando **recibe el repositorio (o el caso de uso ya armado) como parámetro**, con un valor por
defecto que arma el real solo cuando no se lo pasan:

```python
def ejecutar(args: argparse.Namespace, repo: JugadorRepositorio | None = None) -> None:
    if repo is None:
        conexion = SQLiteManager(r.DB_FILE, r.SCHEMA_SQL, r.VISTA_SQL).connect()
        repo = SqliteJugadorRepositorio(conexion)

    dto = CrearJugadorDTO(nombre=args.nombre, apellido=args.apellido, dni=args.dni, anioNacimiento=args.anio)
    caso_uso = RegistrarJugadorUseCase(repo)
    try:
        jugador = caso_uso.ejecutar(dto)
        print(f"Jugador creado: {jugador.nombre} {jugador.apellido} (id={jugador.idJugador})")
    except DNIDuplicadoError as e:
        print(f"Error: {e}")
```

En producción (`main.py`) nadie pasa `repo=`, así que se usa el real. En los tests, siempre se
pasa un Fake. Esto es la misma Inyección de Dependencias del AC2, aplicada un nivel más arriba
(en el comando, no solo en el caso de uso).

---

## 6. `pytest.mark.parametrize` — muchos casos, un solo test

Cuando quieren probar la misma lógica contra varios valores de entrada (por ejemplo, varias
combinaciones inválidas de `JugadorPartido`), repetir el test a mano es ruidoso.
`parametrize` genera un test por cada tupla de valores:

```python
import pytest
from dominio.entidades.partido import JugadorPartido


@pytest.mark.parametrize(
    "t2c, t2l, mensaje_esperado",
    [
        (5, 3, "T2C"),   # convirtió más de lo que lanzó -> debe fallar
        (10, 2, "T2C"),
    ],
)
def test_jugador_partido_t2c_mayor_a_t2l_lanza_valueerror(t2c, t2l, mensaje_esperado):
    with pytest.raises(ValueError, match=mensaje_esperado):
        JugadorPartido(idJugador=1, idPartido=1, idClub=1, t2c=t2c, t2l=t2l, puntos=t2c * 2)
```

`pytest` corre esto como si fueran 2 tests independientes (se ven separados en el reporte de
`-v`), sin duplicar código.

---

## 7. Cobertura (`coverage`) — cómo leerla, no solo cómo correrla

`make run_test` ya corre `pytest -v --cov=src --cov-report=html`, que genera una carpeta
`htmlcov/` navegable (abrir `htmlcov/index.html` en el navegador). Ideas para leerlo bien, no solo
mirar el número total:

- **El % global importa menos que las líneas rojas específicas** — un 85% con las líneas de
  manejo de errores sin cubrir es peor que un 80% donde falta cubrir solo un `print` cosmético.
- Para esta US, presten atención a que el reporte muestre cubiertas **las dos ramas** de cada
  caso de uso: la del camino feliz y la del `except`/`raise` de la excepción de dominio — es común
  escribir solo el test feliz y dejar la rama de error sin cobertura real.
- Cobertura alta **no prueba que la lógica sea correcta** — solo prueba que esa línea se ejecutó
  al menos una vez durante los tests. Un test sin ningún `assert` significativo puede dar 100% de
  cobertura y no estar probando nada. Cobertura es una red para encontrar código que **nadie**
  está probando, no un reemplazo de pensar los casos.

---

## 8. Buenas prácticas rápidas (ya las vienen aplicando, para reforzar)

- **Arrange–Act–Assert**: armar los datos, ejecutar la acción bajo prueba, verificar el
  resultado — en ese orden, como bloques separados (aunque no lo comenten explícitamente, ya es
  el patrón que siguen en `test_repositorios_jugador.py`).
- **Nombres de test descriptivos**: `test_guardar_jugador_dni_duplicado_lanza_excepcion` dice qué
  se prueba y qué se espera con solo leer el nombre — sigan así.
- **Un test, una razón de fallar**: si un test tiene 5 `assert` sobre 5 comportamientos distintos
  y no relacionados, cuando falle no vas a saber cuál sin leer el traceback completo. Está bien
  tener varios `assert` sobre el **mismo** resultado (como ya hacen: `nombre`, `apellido`, `dni`
  del mismo jugador guardado), pero no mezclar comportamientos distintos en un solo test.
- **Tests deterministas**: nada de `datetime.now()` sin fijar, ni `random` sin semilla, dentro de
  un test — si el test puede fallar "a veces" sin que cambie el código, algo anda mal en el test,
  no en el código.
- **Los tests no dependen entre sí**: cada test arma su propio estado desde cero (por eso las
  fixtures de `conftest.py` recrean la conexión en cada test) — nunca un test debería asumir que
  otro corrió antes y dejó algo listo.

---

## 9. Checklist para la US-103, entidad por entidad

Por cada caso de uso nuevo (ver la lista completa en
[el documento de flujo completo](../context_ia/2026-08-29-us103-argparse-comandos-flujo-completo.md#3-orden-de-archivos-a-crear-por-caso-de-uso)):

- [ ] Un test unitario del **camino feliz** en `tests/unit/`, con Fake o Mock.
- [ ] Un test unitario por **cada excepción de dominio** que ese caso de uso pueda lanzar.
- [ ] Si el caso de uso hace más de una operación de escritura (como
      `InscribirClubEnCompetenciaUseCase`, que crea `Inscripcion` + `ListaBuenaFe`), un test que
      confirme la atomicidad (AC5) — típicamente a nivel del **repositorio**, en
      `tests/integration/`, forzando que la segunda operación falle y confirmando que la primera
      tampoco quedó guardada.
- [ ] Un test del **comando CLI** correspondiente, con `capsys`, para el mensaje de éxito y para
      el mensaje de error amigable (sin traceback, confirmando el AC3).
- [ ] Si el comando lista datos (AC4), un test que confirme que la salida pasó por `tabulate`
      (alcanza con buscar algún separador característico de la tabla en el string capturado).
