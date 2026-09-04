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

Utilizá la barra de navegación superior para explorar los diferentes módulos:

* **[Plan de Desarrollo](plan_desarrollo_detallado.md):** Especificación técnica del producto, hitos y requerimientos funcionales.
* **Código y Referencia:**
    * **[Interfaces de Dominio](repositorios_dominio.md):** Contratos de repositorio y entidades del negocio del básquet.
    * **[Persistencia SQLite](repositorios_infraestructura.md):** Implementaciones de acceso a base de datos local.
* **Guías y Arquitectura:** Explicación técnica de la arquitectura Clean/Hexagonal implementada en el proyecto.

---

## Inicio Rápido para Desarrolladores

Para ejecutar las pruebas y validar el entorno:

```bash
# Ejecutar la suite completa de pruebas unitarias
pytest

# Levantar este portal de documentación en local
mkdocs serve
