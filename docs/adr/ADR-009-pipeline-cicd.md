# ADR-009: Pipeline de Integración Continua

- **Estado**: Aprobado (ya implementado)
- **Fecha**: 2026-10-03

## Contexto

El proyecto necesitaba verificación automática de calidad (lint, tipos, tests, cobertura,
seguridad de dependencias) en cada Pull Request, para que el estado del pipeline fuera la única
fuente de verdad sobre si un cambio está en condiciones de mergearse (US-109). A diferencia del
resto de los ADR de este documento, esta decisión **ya se implementó y se usa activamente** —
este ADR formaliza por escrito lo que ya está funcionando en `.github/workflows/MainAction.yml`.

## Alternativas Consideradas

- **GitHub Actions (GitHub-hosted runners):** servicio de CI integrado al mismo lugar donde vive
  el repositorio, sin infraestructura propia que mantener; minutos gratuitos limitados según el
  tipo de repositorio (privado/público).
- **Runners propios (self-hosted):** máquinas propias registradas como runners de GitHub Actions
  (u otro CI). Sin límite de minutos "de GitHub", pero exige mantener esas máquinas (parches,
  disponibilidad, seguridad) — innecesario para el tamaño actual del equipo y del proyecto.
- **Otro proveedor de CI (GitLab CI, CircleCI, etc.):** hubiera significado mover el control de
  versiones o integrar un servicio externo aparte, sin ningún beneficio concreto sobre lo que ya
  ofrece GitHub Actions estando el repositorio en GitHub.

## Decisión Tomada

**GitHub Actions, con runners hosteados por GitHub** (`ubuntu-latest`, `windows-latest`) —
confirmado como el camino definitivo, sin plan de migrar a runners self-hosted. Ya implementado en
`.github/workflows/MainAction.yml`: jobs de auditoría de dependencias (`pip-audit`), detección de
secretos (`gitleaks`), lint y formato (`ruff`), tipos (`mypy --strict`), tests con cobertura en
Linux/Windows/Docker con matriz de Python 3.11 a 3.14 (Windows solo 3.13), disparado en Pull
Request, en `push` a `main`/`develop` y manualmente. Dependencias gestionadas con `uv`
(reproducibles vía `uv.lock`) y actualizadas automáticamente con Dependabot.

## Ventajas y Desventajas

### Ventajas

- Cero infraestructura propia que mantener — el pipeline vive donde ya vive el código.
- Ya probado y funcionando: pip-audit, gitleaks, ruff, mypy, tests multiplataforma y multi-versión
  de Python, todos corriendo hoy en cada PR.
- Dependabot y los hooks de pre-commit usan la misma fuente de verdad (`pyproject.toml`/`uv.lock`)
  que el CI, así que no hay versiones de herramientas desincronizadas entre el equipo y el pipeline.

### Desventajas

- Los minutos de CI de GitHub-hosted son limitados según el plan del repositorio — con la matriz
  actual (4 versiones de Python en Linux + Windows + Docker) una corrida completa son 16
  ejecuciones; si el repositorio es privado, los minutos de Windows cuestan el doble. No es un
  problema hoy, pero es el primer lugar a mirar si el consumo de minutos se vuelve un costo real
  — en ese momento se podría revisar si vale la pena reducir la matriz o migrar partes a un runner
  propio, pero no es una decisión que haga falta tomar ahora.
- Todavía faltan, de la auditoría de `docs/ideas-aprendizaje.md` §8.16 (ya convertidas en AC6-AC8
  de la US-109): job agregador + _required status checks_, `ruff format --check` y el smoke test
  de la CLI — el pipeline funciona, pero todavía no bloquea un merge con el CI en rojo.
