# Pull Request — app_estadisticas

> [!IMPORTANT]
> Antes de pedir review:
> - linkeá la tarea/issue correspondiente
> - asignate esta PR
> - verificá que el cambio corra localmente (`make` / scripts)
> - si hay cambios de **cálculo estadístico**, adjuntá caso de prueba con números
> - si hay cambios de **DB**, adjuntá migración + plan de rollback
> - pedí revisión a quien corresponda (Data/Backend/DB)
> - borrá todo este bloque antes de abrir la PR

---

## Tipo de cambio
<!-- Marcá al menos una opción para ayudar al reviewer a entender la naturaleza del cambio -->
- [ ] Feature
- [ ] Bugfix
- [ ] Refactor
- [ ] Tests
- [ ] Documentation
- [ ] Performance
- [ ] Build / CI
- [ ] Chore
- [ ] Database / Migration
- [ ] Stats / Metrics

---

## Issue / tarea relacionada
<!-- Obligatorio: linkear la tarea o issue asociada.
Usar referencias como:
- Closes #12
- Fixes #8
- Related #21 -->
- Closes #
- Related #

---

## Resumen del cambio
<!-- TL;DR (2 a 5 líneas). Que se entienda sin leer el diff. -->
Este PR:

-
-

---

## Problema / motivación
<!-- Explicá qué problema resuelve (qué fallaba / qué faltaba / por qué era necesario). -->
Contexto
-

Problema observado
-

Resultado esperado
-

---

## Solución implementada
<!-- Explicá el enfoque técnico elegido sin repetir el diff línea por línea.
Mencionar decisiones y trade-offs. -->
Decisiones principales
-

-
-

Componentes / módulos clave
<!-- Ejemplos: ingestión de stats, cálculo de métricas, API, persistencia, reportes. -->
-

-
-

---

## Cambios incluidos
<!-- Lista concreta y escaneable. -->
-
-
-
-

---

## Consideraciones técnicas (Python / Java / Go)
<!-- Completar lo que aplique. Si no aplica, marcá "No aplica". -->
- [ ] No aplica
- [ ] Tipado / type hints revisados (Python)
- [ ] Formato y lint OK (black/ruff/flake8/etc.)
- [ ] Manejo de errores y logs (sin prints temporales)
- [ ] Contratos/API estables (no rompe consumidores)
- [ ] Performance considerada (loops, queries, uso de memoria)
- [ ] Código duplicado evitado / buena modularidad
- [ ] Versionado/compatibilidad (si hay cambios públicos)

Detalle adicional
-

---

## Métricas / estadísticas (si aplica)
<!-- Obligatorio si tocás fórmulas, agregados, reportes o "advanced stats". -->
- [ ] No aplica
- [ ] Métrica(s) nueva(s)
- [ ] Corrección de métrica existente
- [ ] Cambio de definición (breaking)

Métrica(s) afectada(s)
-

Definición / fórmula
-

Variables requeridas y fuente de datos
-

Caso de prueba con números (input → output esperado)
-

---

## Cambios en base de datos (si aplica)
<!-- Obligatorio si agregás/modificás tablas, columnas, índices o queries críticas. -->
- [ ] No aplica
- [ ] Incluye migración
- [ ] Incluye seeds / datos de prueba
- [ ] Incluye rollback

Detalle (schema/índices/constraints)
-

Plan de migración / backfill
-

Plan de rollback
-

---

## Cómo probar este cambio
<!-- Pasos concretos y reproducibles: setup, comandos, endpoints, datos de ejemplo.
Un reviewer o tester debería poder validar sin preguntarte. -->
1.
2.
3.

### Resultado esperado
-

---

## Evidencia
<!-- Obligatorio cuando haya cambios visibles o resultados verificables.
Podés adjuntar screenshots, outputs de consola, JSON de requests/responses, logs, etc. -->
- [ ] No aplica
- [ ] Capturas adjuntas
- [ ] Logs adjuntos
- [ ] Output de consola adjunto
- [ ] JSON de request/response adjunto
- [ ] Video/GIF adjunto

Evidencia
-

---

## Testing realizado
<!-- Marcar lo que realmente se hizo. -->
- [ ] Corre localmente en mi entorno
- [ ] Se agregaron o actualizaron tests unitarios
- [ ] Se agregaron o actualizaron tests de integración
- [ ] Los tests existentes siguen pasando
- [ ] Validación manual (happy path)
- [ ] Casos borde / errores probados
- [ ] No aplica agregar tests (justificar abajo)

Detalle
-

---

## Checklist del autor
<!-- Disciplina mínima antes de pedir review. -->
- [ ] Linkeé la issue / tarea correspondiente
- [ ] Me asigné esta PR
- [ ] El cambio tiene un objetivo claro y acotado
- [ ] No mezclé cambios no relacionados
- [ ] Revisé mi propio diff antes de pedir review
- [ ] El cambio corre localmente
- [ ] Actualicé tests si correspondía
- [ ] Actualicé documentación si correspondía
- [ ] No dejé código muerto, prints temporales o TODOs sin issue
- [ ] Nombres claros (variables/funciones/métodos)
- [ ] La solución respeta la modularidad del proyecto

---

## Checklist de review
<!-- Ajustá roles según tu equipo. Si sos solo, podés simplificar esta sección. -->
- [ ] Review técnica realizada
- [ ] Review de métricas/estadística (si aplica)
- [ ] Review de DB/migraciones (si aplica)

Reviewer(s):
<!--Arrobar a los reviewers-->
- R1:
- R2:
- R3:

---

## Notas para el reviewer
<!-- Para guiar la revisión y ahorrar tiempo. -->
Orden sugerido de revisión:
1.
2.
3.

Puntos donde quiero feedback
-

-

Dudas abiertas
-
