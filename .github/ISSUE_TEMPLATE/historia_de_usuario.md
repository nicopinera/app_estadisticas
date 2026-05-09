---
name: Historia de Usuario
about: Plantilla técnica para implementar una US siguiendo Arquitectura Hexagonal
title: "[US] - "
labels: task
assignees: ""
---

### 📝 Narrativa

**Como** [rol]
**Quiero** [acción]
**Para** [beneficio]

### 🏗 Especificación por Capas

#### 🔴 Capa de Dominio (Pureza)

- **Entidades:** `@dataclass` ...
- **Interfaces (Ports):** `Protocol` ...
- **Excepciones:** `domain/exceptions.py` ...
- **Validaciones:** Lógica en `__post_init__`

#### 🔵 Capa de Aplicación (Casos de Uso)

- **Caso de Uso:** `UseCase` que orquesta la lógica.
- **DTOs:** Objetos de transferencia de datos.

#### 🟢 Capa de Infraestructura (Adaptadores)

- **Persistencia:** Repositorios concretos (SQLite).
- **UI:** Comandos CLI o pantallas Flet.
- **Servicios Externos:** Hashing, PDF, etc.

### 📜 Criterios de Aceptación (AC)

- [ ] **AC1:** ...
- [ ] **AC2:** ...

### 🧪 Plan de Pruebas

- [ ] **Unitarias:** Probar lógica de negocio y entidades con Mocks.
- [ ] **Integración:** Probar persistencia real en DB `:memory:`.

### ✅ Definición de Hecho (DoD)

- [ ] Arquitectura respetada (Domain no importa Infrastructure).
- [ ] Cobertura de tests aceptable.
- [ ] SQL verificado (si aplica).
- [ ] Docstrings incluidos.
