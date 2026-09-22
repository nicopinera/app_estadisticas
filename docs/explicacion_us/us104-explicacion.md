# US-104 explicada en profundidad — Autenticación y Sesión Local

> Documento de referencia conceptual, no un registro de sesión de trabajo. Explica la US-104 como
> si todavía no se hubiera tocado nada de lo que pide — incluyendo los conceptos de seguridad y
> sesión que da por sabidos — y deja marcadas, en el punto exacto del flujo donde hay que
> resolverlas, las preguntas de diseño que el plan de desarrollo no responde. Pensado para
> consultarse mientras se construye la US, no solo para leerse una vez.
>
> **Estado verificado hoy, para que el documento arranque con la foto real:**
>
> - La entidad `Usuario` ([usuario.py](../../src/dominio/entidades/usuario.py)) **ya existe**, pero
>   solo tiene `nombre`, `email`, `pw`, `idUsuario`. No tiene `salt` como campo separado, y
>   `__post_init__` solo valida **tipos** (`isinstance` + `TypeError`), no valores — a diferencia de
>   `Club`/`Jugador`/etc. de la US-103, acá no hay ningún `DatoInvalidoError` todavía (nombre vacío,
>   email con formato inválido, contraseña corta no se rechazan hoy).
> - `UsuarioRepositorio` ([usuario_repositorio.py](../../src/dominio/repositorios/usuario_repositorio.py))
>   y su implementación `SqliteUsuarioRepositorio`
>   ([sqlite_usuario_repositorio.py](../../src/infraestructura/repositorios/sqlite_usuario_repositorio.py))
>   **ya existen y funcionan**: `encontrar_por_mail`, `encontrar_por_id`, `guardar`. Importante: usan
>   nombres en español, **distintos** de los que menciona el texto de la US (`get_by_email`,
>   `get_by_id`, `save`) — se sigue la convención real del proyecto, no la del texto.
> - La tabla `usuario` en `schema.sql` **ya existe**, con la columna `contrasenia` (no `pw` —
>   ese es el nombre del atributo Python, el de la columna SQL es distinto). Hoy esa columna
>   guarda lo que sea que se le pase como `pw`; **todavía no hay ningún hashing**, se guardaría en
>   texto plano si se usara tal cual.
> - `src/dominio/exceptions.py` ya tiene `UsuarioNoEncontradoError` y `CredencialesInvalidasError`
>   (reusables tal cual). **Falta** `EmailYaRegistradoError`, que la US pide.
> - `CambiarClubActivoUseCase` ([cambiar_club_activo.py](../../src/aplicacion/casos_uso/cambiar_club_activo.py))
>   **ya está implementado** (nació en la US-103) y deliberadamente **no** guarda nada en sesión —
>   solo valida que el club exista y pertenezca al usuario. Guardar el club elegido es responsabilidad
>   de esta US.
> - `club list` ([club_list.py](../../src/infraestructura/ui/cli/commands/club_list.py)) hoy
>   recibe `--id-usuario` como flag explícito (provisorio). Esta US tiene que reemplazarlo por la
>   lectura del usuario desde la sesión.
> - **No existe todavía absolutamente nada de:** `SessionManager`, `PasswordHasher`, DTOs de auth,
>   casos de uso `RegistrarEntrenadorUseCase`/`LoginLocalUseCase`, ni los comandos CLI
>   `auth_register`, `auth_login`, `auth_logout`, `club_select`. Tampoco hay subparser `auth` en
>   `src/main.py` todavía.

---

## 1. Conceptos necesarios antes de empezar

La US-104 da por sabidos varios conceptos de seguridad y de manejo de estado que no aparecieron
en la US-103. Antes de tocar código conviene tenerlos claros, porque varias de las preguntas de
las secciones siguientes dependen de entenderlos bien.

### 1.1 Hash de contraseña

Un **hash** es una función que toma un dato (acá, la contraseña en texto plano) y devuelve una
cadena de longitud fija, de forma que:

- Es **prácticamente imposible** reconstruir la contraseña original a partir del hash (a
  diferencia de "cifrar", que sí se puede revertir con la clave correcta — un hash **no** se
  revierte).
- La **misma** contraseña siempre produce el **mismo** hash (con el mismo salt — ver 1.2), lo cual
  permite verificar un login sin guardar la contraseña: al loguearse, se hashea lo que el usuario
  escribió y se compara contra el hash guardado. Si coinciden, la contraseña era correcta.

Por eso "nunca guardar contraseñas en texto plano" (AC1 de la US-104) significa en la práctica
"guardar solo el resultado de hashear la contraseña, nunca la contraseña en sí".

### 1.2 Salt — y la diferencia entre fijo y dinámico

Si dos usuarios distintos eligen la misma contraseña (`"123456"`, por ejemplo) y se hashea tal
cual, ambos quedarían con el **mismo hash guardado** en la base — lo cual filtra información (un
atacante que ve la base sabe que esos dos usuarios comparten contraseña) y además hace posible
precalcular hashes de contraseñas comunes de antemano (**rainbow tables**) y buscarlos por
coincidencia exacta.

El **salt** es un valor aleatorio que se mezcla con la contraseña _antes_ de hashear
(`hash(contraseña + salt)`), así el mismo password produce un hash distinto según el salt usado.
Hay dos formas de usarlo, y la diferencia importa:

- **Salt fijo:** un único valor, igual para todos los usuarios (por ejemplo, guardado en un
  archivo de configuración o hardcodeado). Evita que un hash filtrado se busque directamente en
  una rainbow table genérica, pero **no** evita que dos usuarios con la misma contraseña tengan el
  mismo hash — y si ese salt único se filtra, alcanza con una sola rainbow table adaptada a ese
  salt para atacar a **todos** los usuarios a la vez.
- **Salt dinámico:** un valor distinto **por usuario**, generado al registrarse y guardado junto
  al hash (no hace falta que el salt sea secreto, solo que sea único). Con esto, aunque dos
  usuarios compartan contraseña, sus hashes guardados son distintos, y un atacante tiene que
  atacar usuario por usuario en vez de una sola vez para toda la tabla. Es la práctica estándar
  recomendada hoy.

**Por qué esto importa para esta US en particular:** el propio plan de desarrollo se contradice
sobre cuál usar en v0.1 (ver la pregunta del Paso 3, sección 4).

### 1.3 `pbkdf2_hmac`/SHA-256 genérico vs. `bcrypt`/`argon2`

SHA-256 (y en general los algoritmos de la familia usada por `hashlib`) están diseñados para ser
**rápidos** — son hashes de propósito general (integridad de archivos, checksums), y esa
velocidad es mala para contraseñas: un atacante con hardware dedicado puede probar miles de
millones de combinaciones por segundo. `pbkdf2_hmac` mejora esto aplicando el hash muchas veces en
cadena (iteraciones configurables), lo cual ya ayuda bastante y es razonable para un v0.1.

`bcrypt` y `argon2` son **diseñados específicamente para contraseñas**: son deliberadamente lentos
y, en el caso de `argon2`, también consumen memoria a propósito — ambas cosas dificultan mucho más
los ataques de fuerza bruta masiva, incluso con hardware especializado. Por eso el plan habla de
arrancar con algo simple (`pbkdf2_hmac`) y migrar más adelante a una de estas dos librerías.

### 1.4 Sesión persistente / "estado de sesión"

Una app de escritorio o un sitio web típico corre como **un proceso continuo**: el estado
(usuario logueado, club activo) puede vivir en memoria mientras el proceso está vivo. Una CLI,
en cambio, **arranca un proceso nuevo por cada comando** (`stats club list`, `stats jugador add`,
etc. son ejecuciones independientes) — cuando el proceso termina, cualquier variable en memoria se
pierde. Por eso, para que "estar logueado" sobreviva entre un comando y el siguiente, ese estado
tiene que **persistirse en disco** (archivo o base de datos) y leerse de nuevo al arrancar cada
comando. Esa es la razón de ser del `SessionManager`.

### 1.5 Token de sesión y expiración

En una sesión **web** típica, el servidor genera un **token** aleatorio al loguearse, se lo
entrega al navegador (en una cookie), y guarda solo un **hash** de ese token en el servidor
(`session_token_hash`) junto con una fecha de vencimiento (`expires_at`). En cada pedido, el
navegador manda el token, el servidor lo hashea y compara — así, si alguien roba la base de
datos del servidor, no puede reconstruir tokens válidos, y aunque robe el token, deja de servir
después de `expires_at`.

Este esquema tiene sentido cuando **el cliente y el servidor son procesos distintos, en máquinas
distintas**, con una red insegura de por medio. En la US-104, el "cliente" y el "servidor" son el
mismo proceso en la misma máquina, leyendo el mismo archivo local — no hay red, no hay otro
dispositivo al que entregarle un token. Por eso conviene evaluar si este esquema aplica acá o es
sobrealcance (ver la pregunta del Paso 5, sección 4).

### 1.6 Club activo / contexto activo

Un mismo entrenador puede pertenecer a más de un club (tabla `usuarioClub`, relación N:M). Casi
todos los comandos operativos (cargar un partido, listar jugadores) necesitan saber "¿de qué club
estamos hablando?". En vez de pedir `--club-id` en cada comando, se guarda un **club activo** en
la sesión — el mismo patrón que el "proyecto activo" de un IDE o el directorio actual de una
shell (`cd`): se fija una vez y el resto de los comandos lo asumen hasta que se cambie.

### 1.7 Repaso rápido: DTO, caso de uso, repositorio

Estos patrones ya se usaron en la US-103 y la US-104 los reutiliza sin volver a explicarlos:

- **Repositorio:** interfaz (`ABC`) en `dominio/repositorios/` que declara qué operaciones existen
  sobre los datos (`guardar`, `encontrar_por_mail`), sin decir cómo — la implementación SQLite
  vive en `infraestructura/repositorios/`.
- **Caso de uso:** una clase en `aplicacion/casos_uso/`, un archivo por acción, que recibe sus
  repositorios por constructor (inyección de dependencias) y expone un único método `ejecutar(...)`
  con la lógica de negocio de esa acción puntual.
- **DTO:** una dataclass simple, sin lógica, que transporta datos entre la CLI y los casos de uso
  (de entrada: lo que el usuario tipeó; de salida: lo que se necesita mostrar).

---

## 2. Qué pide la US-104, completa

**Esfuerzo:** M (3-5 días) · **Prioridad:** Alta · **Dependencias:** US-103.

**Objetivo funcional:** permitir el registro y acceso seguro de entrenadores al sistema,
manteniendo un estado de sesión persistente entre ejecuciones de la CLI, para no pedir
credenciales ni el club activo en cada comando.

**Narrativa:** como usuario, quiero un sistema de login local que proteja mis datos y mantenga mi
sesión entre ejecuciones de la CLI.

**Las tres capas que toca, resumido:**

| Capa            | Qué agrega esta US                                                                             |
| --------------- | ---------------------------------------------------------------------------------------------- |
| Dominio         | Nada nuevo en entidades (`Usuario` ya existe) — sí faltan reglas de validación y una excepción |
| Aplicación      | Casos de uso `RegistrarEntrenadorUseCase`, `LoginLocalUseCase` + servicio `SessionManager`     |
| Infraestructura | `PasswordHasher`, persistencia de sesión, 4 comandos CLI nuevos                                |

**Qué reusa de la US-103** (dependencia explícita): la convención de un archivo por acción en
`commands/`, `src/main.py` como composition root (se le agregan subparsers, no se recrea), el
patrón `ejecutar(args, repo=None)` de cada comando, y — puntualmente — `CambiarClubActivoUseCase`,
que ya valida la pertenencia del club al usuario; esta US solo tiene que sumarle la persistencia
en sesión.

**Los 4 Criterios de Aceptación:**

1. **AC1 — Seguridad de credenciales:** las contraseñas nunca se guardan ni se loguean en texto
   plano; hashing determinista con salt (ver sección 1.1-1.3).
2. **AC2 — Persistencia de sesión:** la sesión sobrevive al cierre de la CLI; al reiniciar,
   `is_authenticated()` devuelve `True` si había sesión activa.
3. **AC3 — Manejo de contexto:** el archivo/registro de sesión recuerda el club activo actual.
4. **AC4 — Validaciones:** email único; contraseña con requisitos mínimos (≥6 caracteres en v0.1;
   ≥12 con complejidad en v1.0, ver US-403).

**Reglas de negocio:**

- `clear_session()` es idempotente (llamarla sin sesión activa no debe fallar).
- `set_active_club()` falla si no hay sesión previa.
- Los comandos protegidos ejecutan `require_auth()` y `require_active_club()` según corresponda.

**Base de datos:** tabla `usuario` (`idUsuario`, `nombre`, `email`, `contrasenia`) — ya existe, sin
cambios de esquema previstos por el texto de la US.

**Testing mínimo que pide la US:**

- Unitarias: hash y verificación de contraseñas; lógica de registro/login con repositorios mock.
- Integración: persistencia de sesión con archivo temporal; flujo completo registro → login →
  sesión usando DB `:memory:`.

---

## 3. Por qué importa esta US

Hasta la US-103, cada comando pedía explícitamente `--id-usuario` (`club_list.py` lo hace hoy) —
funcional para probar, pero incómodo e inseguro para el uso real: cualquiera podría pasar el ID de
otro usuario sin ninguna verificación. La US-104 resuelve dos problemas a la vez:

1. **Autenticación real:** verificar que quien ejecuta un comando efectivamente demostró conocer
   la contraseña del usuario, no solo un ID arbitrario.
2. **Contexto persistente:** evitar repetir `--id-usuario` y (una vez que exista) `--club-id` en
   cada comando, guardando "quién soy" y "con qué club trabajo ahora" en un lugar que sobrevive
   entre ejecuciones — el mismo patrón que el "proyecto activo" de un IDE (sección 1.6).

Sin esta US, **ningún comando protegido de las US siguientes (US-105, US-106) tiene una forma
real de saber quién es el usuario ni qué club está activo** — hoy esa información se pasa a mano
como flag, algo que las US siguientes ya dan por reemplazado.

---

## 4. Paso a paso de construcción, en el orden en que conviene encararla

### Paso 1 — Dominio: entidad `Usuario`

Hoy `Usuario` (sección "Estado verificado hoy") tiene `nombre`, `email`, `pw`, `idUsuario`, con
`__post_init__` que solo valida tipos. Para esta US hay que decidir varias cosas de forma:

> **❓ Pregunta 1 — ¿Cómo queda el campo de contraseña en la entidad?**
> El texto de la US habla de `password_hash` y `salt` como si fueran dos campos separados de
> `Usuario`. Hoy solo existe `pw` (mapeado a la columna `contrasenia`). Opciones: (a) renombrar
> `pw` a `password_hash` y agregar un campo `salt` nuevo (dos columnas en la tabla `usuario`,
> requiere migrar el esquema); (b) mantener un solo campo (`pw` o renombrado) donde el
> `PasswordHasher` guarde el hash y el salt **juntos** en un único string, como hacen `bcrypt` y
> `pbkdf2_hmac` en formato estándar (el salt no necesita ser secreto, alcanza con poder
> extraerlo del string guardado al verificar). La opción (b) no requiere tocar `schema.sql`.

> **❓ Pregunta 2 — ¿Se agregan validaciones de valor a `Usuario`?**
> El resto de las entidades de la US-103 (`Club`, `Jugador`, etc.) ya tienen `DatoInvalidoError`
> para nombre vacío, DNI inválido, etc. `Usuario` todavía no valida que `nombre`/`email` no estén
> vacíos, ni el formato del email. ¿Se suma esa validación acá (consistente con el resto del
> dominio) o queda para una US de seguridad posterior (US-403, que ya se menciona para la
> complejidad de contraseña en v1.0)?

### Paso 2 — Dominio: excepción faltante

`EmailYaRegistradoError` no existe en `exceptions.py` — agregarla, hija de `ErrorDeDominio`, junto
a las que ya están (`UsuarioNoEncontradoError`, `CredencialesInvalidasError`, ambas reusables tal
cual para `LoginLocalUseCase`).

### Paso 3 — Infraestructura/seguridad: `PasswordHasher`

> **❓ Pregunta 3 — Contradicción de ADR-006 sobre salt fijo vs. dinámico en v0.1.**
> El texto de la propia US-104 dice que v0.1 puede arrancar con `hashlib.pbkdf2_hmac`/SHA-256
> "con salt **dinámico**". La tabla de ADRs del mismo documento dice "v0.1: SHA-256 con salt
> **fijo**. v1.0: migrar a bcrypt con salt dinámico". Son contradictorios entre sí. Dado lo
> explicado en la sección 1.2, salt dinámico es la opción más segura y no cuesta más
> implementarla desde el arranque (`os.urandom` + guardarlo junto al hash, ver Pregunta 1) — hay
> que confirmar con el equipo cuál de las dos fuentes es la vigente antes de escribir el código,
> y si se confirma, corregir la contradicción en `plan_desarrollo_detallado.md`.

`PasswordHasher` expone solo dos métodos públicos: `hash(password) -> str` y
`verify(password, hash) -> bool`. Vive en `src/infraestructura/security/password_hasher.py`.

### Paso 4 — Aplicación: `RegistrarEntrenadorUseCase` y `LoginLocalUseCase`

`RegistrarEntrenadorUseCase`: valida que el email no esté registrado (`EmailYaRegistradoError` si
ya existe, usando `UsuarioRepositorio.encontrar_por_mail`), hashea la contraseña con
`PasswordHasher` y guarda el usuario.

`LoginLocalUseCase`: busca el usuario por email, verifica la contraseña con `PasswordHasher`
(`CredencialesInvalidasError` si no coincide o el usuario no existe — sin distinguir cuál de las
dos cosas falló, para no filtrar si un email está registrado o no), y devuelve un `SessionDTO`.

> **❓ Pregunta 4 — ¿El registro asocia al usuario a un club, o queda pendiente por completo?**
> Ni la US-103 ni la US-104 lo dicen, pero hay un gap real en el código: `CrearClubUseCase`
> ([crear_club.py](../../src/aplicacion/casos_uso/crear_club.py)) crea el club y **nunca inserta
> en la tabla `usuarioClub`** (la relación N:M entre usuario y club, con `rolEntrenador`). Sin ese
> vínculo, `club list` (que hace `JOIN usuarioClub`) y el futuro `club select` de esta misma US no
> van a encontrar **ningún** club para **ningún** usuario real — aunque el login funcione
> perfecto. Falta decidir quién llena `usuarioClub`: ¿`club add` pasa a recibir el usuario de la
> sesión y lo vincula automáticamente como entrenador al crear el club? ¿Es un caso de uso nuevo
> separado (`VincularUsuarioClubUseCase`)? Sin resolver esto, el flujo de punta a punta
> (registrarse → loguearse → crear o ver un club → seleccionar club activo) no se puede probar
> completo aunque cada pieza individual esté bien implementada.

### Paso 5 — Aplicación: `SessionManager`

Este es el servicio central de la US: expone `load_session`/`get_current`, `save_session`,
`is_authenticated`, `clear_session`/`destroy`, `set_active_club`/`set_club_activo`.

> **❓ Pregunta 5 (la central) — ¿Persistir la sesión en un JSON o en la misma base SQLite?**
>
> El plan da por sentado un archivo JSON oculto, pero vale la pena confirmarlo con los dos lados:
>
> |               | Archivo JSON local                                                                                                                                                                                                                                                                                                                                                | Tabla en la misma DB SQLite                                                                                                                                                                                                         |
> | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
> | **A favor**   | Es el mecanismo estándar para este tipo de estado de CLI (`~/.aws/credentials`, `~/.netrc`, `~/.docker/config.json`); no agrega una transacción de DB a cada comando; se puede borrar a mano para "desloguearse a la fuerza"; no compite por locks con la base de datos SQLite (que ya tiene problemas de concurrencia documentados en otras partes del proyecto) | Un solo lugar de verdad para todo el estado de la app; no hay que manejar rutas de archivo por SO ni permisos de filesystem por separado; los tests de integración ya usan DB `:memory:`, reusable también para esto                |
> | **En contra** | Hay que manejar la ruta correcta por sistema operativo (ver Pregunta 6) y los permisos del archivo a mano                                                                                                                                                                                                                                                         | Mezcla estado transitorio de sesión (que no tiene sentido versionar/respaldar) con datos persistentes de negocio en la misma base; complica el backup/restore de la DB (US-402) si la sesión de la máquina local queda embebida ahí |
>
> Dado que el propio plan ya especifica una carpeta de datos de la app (`~/.statspro/`) y que el
> testing mínimo que pide la US explícitamente dice "persistencia de sesión con archivo
> temporal" (no con DB `:memory:`), el JSON parece la intención original — pero es una decisión
> de diseño real que conviene dejar explícita antes de programar, no asumida en silencio.

> **❓ Pregunta 6 — ¿Cuál es la ruta correcta del archivo de sesión?**
> El documento da dos rutas distintas en dos secciones distintas: la sección de arquitectura dice
> `~/.statspro/session.json` (o `./data/session.json` en desarrollo); el texto de la propia
> US-104 dice `~/.statspro/session.json` **o** `~/.statspro_session.json`. Hay que fijar una sola
> ruta canónica (probablemente con `pathlib.Path.home()`, que en Windows resuelve a
> `%USERPROFILE%`, para que funcione igual en el entorno de desarrollo de este proyecto).

> **❓ Pregunta 7 — ¿Hace falta token de sesión con expiración, o alcanza con lo que pide `SessionDTO`?**
> `SessionDTO` (tal como lo define el texto de la US) solo tiene `usuario_id`, `email`,
> `club_activo_id`. Pero la sección de arquitectura describe una estructura de archivo de sesión
> con además `session_token_hash` y `expires_at` — el esquema típico de sesión web explicado en
> la sección 1.5. Como se explicó ahí, ese esquema tiene sentido cuando cliente y servidor son
> procesos distintos en máquinas distintas; acá el archivo lo lee y escribe el mismo proceso en
> la misma máquina. ¿Se implementa igual (por si en algún hito futuro la CLI deja de ser
> puramente local) o se simplifica a los campos que realmente pide `SessionDTO`, sin
> token/expiración, para no construir algo que no se va a usar?

### Paso 6 — Infraestructura/CLI: comandos nuevos

`auth_register.py`, `auth_login.py`, `auth_logout.py`, `club_select.py` (este último reusa
`CambiarClubActivoUseCase` para validar y le suma guardar el club en el `SessionManager`),
siguiendo la convención ya establecida de un archivo por acción en
`src/infraestructura/ui/cli/commands/`, registrados como subparsers nuevos en
`construir_parser()` de `src/main.py`.

> **❓ Pregunta 8 — ¿Cómo llegan los comandos a la instancia de `SessionManager`?**
> El patrón actual (`ejecutar(args, repo=None)`, cada comando arma sus propias dependencias si no
> se las inyectan, composition root en `main.py`) no dice todavía dónde vive la instancia de
> `SessionManager` ni cómo se comparten `require_auth()`/`require_active_club()` entre comandos
> distintos sin duplicar código ni romper el patrón de "un archivo por acción, sin acoplarse
> entre sí". Posible resolución: que cada comando arme su propio `SessionManager` igual que arma
> su propio repositorio (mismo patrón que ya usan, consistente), y que `require_auth()`/
> `require_active_club()` vivan como funciones sueltas en un módulo compartido (por ejemplo
> `ui/cli/auth_guards.py`) que reciban el `SessionManager` ya armado — a confirmar antes de
> escribir el primer comando protegido.

### Paso 7 — Infraestructura/CLI: sacar el `--id-usuario` provisorio

`club_list.py` (y cualquier otro comando que hoy reciba `--id-usuario` a mano) pasa a leer el
usuario desde la sesión vía `require_auth()`, dejando de aceptar el flag provisorio.

### Paso 8 — Testing

Cubrir lo que pide el texto de la US: hash/verify de `PasswordHasher` (unitario), registro/login
con `UsuarioRepositorio` mock (unitario, camino feliz + `EmailYaRegistradoError` +
`CredencialesInvalidasError`), persistencia de sesión con archivo temporal (integración, cubre
las Preguntas 5-7 una vez resueltas), y el flujo completo registro → login → `club select` →
sesión con DB `:memory:` (integración).

---

## 5. Relación con la US-105

La US-105 (Carga Atómica de Partido) declara depender de US-103 y US-104, pero su propio texto no
explica **por qué** necesita la US-104 más allá de "el partido no se puede cargar sin sesión" —
no está escrito explícitamente en ningún lado.

> **❓ Pregunta 9 — ¿De dónde sale el club local/visitante al cargar un partido?**
> Ni la US-104 ni la US-105 lo definen. `stats game add` es un flujo interactivo multi-paso que
> registra un partido entre dos clubes — ¿ambos clubes se piden siempre como datos explícitos del
> formulario (porque un partido puede ser entre el club activo y un rival externo), o alguno de
> los dos (el "local", probablemente) se infiere automáticamente del club activo de la sesión que
> arma esta US? La respuesta condiciona qué necesita exponer `SessionManager` (¿alcanza con
> `club_activo_id`, o hace falta algo más) y conviene dejarla planteada acá, ya que quien diseñe
> la US-105 va a depender directamente de esta.

---

## 6. Checklist final de preguntas abiertas

En el mismo orden en que aparecieron:

1. ¿`pw`/`password_hash` y `salt` como campos separados en `Usuario`, o un solo campo con hash+salt combinados? (Paso 1)
2. ¿Se agregan validaciones de valor (`DatoInvalidoError`) a `Usuario`, o queda para US-403? (Paso 1)
3. Contradicción de ADR-006: ¿salt fijo o dinámico en v0.1? (Paso 3)
4. ¿Quién vincula usuario y club en `usuarioClub` — falta en `CrearClubUseCase` de US-103, no contemplado en ninguna US? (Paso 4)
5. ¿Sesión persistida en archivo JSON o en la misma base SQLite? (Paso 5)
6. ¿Cuál es la ruta canónica del archivo de sesión — corregir la inconsistencia entre las dos secciones del plan? (Paso 5)
7. ¿Hace falta `session_token_hash`/`expires_at`, o alcanza con los campos de `SessionDTO`? (Paso 5)
8. ¿Cómo acceden los comandos CLI a `SessionManager` y dónde viven `require_auth()`/`require_active_club()`? (Paso 6)
9. En la futura US-105, ¿el club local/visitante del partido sale de argumentos explícitos o del club activo de la sesión? (sección 5)
