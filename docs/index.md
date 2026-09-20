# Sistema de Estadísticas de Básquetbol (Córdoba)

Bienvenido a la documentación oficial del sistema de registro y procesamiento de estadísticas para torneos y clubes de básquetbol de la provincia de Córdoba.

---

## Propósito del Proyecto

El sistema centraliza la gestión deportiva y técnica de la competencia:
* **Entidades y Clubes:** Registro de clubes afiliados, categorías formativas y de primera división.
* **Listas de Buena Fe:** Carga, validación de jugadores habilitados e inscripciones por torneo.
* **Estadísticas de Juego:** Procesamiento de planillas oficiales, boxscores, faltas y métricas de rendimiento por jugador y equipo.

---

## Estructura de la Documentación

Estas son las secciones principales:

* **[Plan de Desarrollo](plan_desarrollo_detallado.md):** Especificación técnica del producto, hitos y requerimientos funcionales.
* **Código y Referencia:**
    * **[Interfaces de Dominio](repositorios_dominio.md):** Contratos de repositorio y entidades del negocio del básquet.
    * **[Persistencia SQLite](repositorios_infraestructura.md):** Implementaciones de acceso a base de datos local.
* **[Guías técnicas](info_modulo/):** Arquitectura Clean/Hexagonal, casos de uso, patrón Command, testing, Docker y más (guías numeradas).

---

## Inicio Rápido para Desarrolladores

Para instalar las dependencias y ejecutar las pruebas (necesitás [uv](https://docs.astral.sh/uv/); el detalle está en el [RUNBOOK](../RUNBOOK.md)):

```bash
uv sync
uv run pytest
```
