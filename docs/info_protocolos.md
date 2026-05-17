# Protocolo en python

En el contexto de Python y de la Arquitectura Limpia que estamos aplicando para StatsPro, cuando hablo de "Protocolo" me refiero específicamente a typing.Protocol.

Es la herramienta que usamos para definir las Interfaces (Puertos) en la capa de Dominio. En otros lenguajes como Java o C#, usarías una interface; en Python, el Protocol permite implementar lo que se conoce como Static Duck Typing (Tipado estructural).

Aquí te explico por qué es la pieza clave para que tu aplicación sea robusta y fácil de testear:

## El Contrato (En src/domain/interfaces/)

El Protocol define qué métodos debe tener una clase para ser considerada un "Repositorio", sin importar cómo funcione por dentro. El Dominio no sabe que existe SQLite; solo sabe que existe algo que cumple con este contrato.

```python
from typing import Protocol, Optional
from domain.entities.jugador import Jugador


class JugadorRepository(Protocol):
    """Contrato que define cómo se deben persistir los jugadores."""

    def save(self, jugador: Jugador) -> None:
        """Guarda un jugador en el sistema."""
        ... # Los puntos suspensivos son literales en Python para protocolos

    def get_by_dni(self, dni: int) -> Optional[Jugador]:
        """Busca un jugador por su DNI."""
        ...
```

## La Implementación (En src/infrastructure/persistence/)

Aquí es donde creas la clase concreta que realmente habla con la base de datos. Lo interesante es que no necesitas heredar explícitamente del Protocolo (aunque puedes hacerlo para que el linter te ayude). Si la clase tiene los mismos métodos, Python (y herramientas como MyPy o PyCharm) entenderán que "cumple el protocolo".

```python
class SQLiteJugadorRepository:
    def __init__(self, db_connection):
        self.db = db_connection

    def save(self, jugador: Jugador) -> None:
        # Lógica real de SQL: INSERT INTO jugador ...
        pass

    def get_by_dni(self, dni: int) -> Optional[Jugador]:
        # Lógica real: SELECT * FROM jugador WHERE dni = ...
        pass
```