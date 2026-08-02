# Diagrama Utiles

## Diagrama de clases

```mermaid
classDiagram
    SqliteClubRepositorio --|> ClubRepositorio : Implementa
    SqliteJuegoRepositorio --|> JuegoRepositorio : Implementa
    SquliteJugadorRepositorio --|> JugadorRepositorio : Implementa
    SqliteUsuarioRepositorio --|> UsuarioRepositorio : Implementa
    SqliteCompetenciaRepositorio --|> CompetenciaRepositorio : Implementa
    ClubRepositorio ..> Club : usa
    ClubRepositorio ..> UsuarioClub : usa
    CompetenciaRepositorio ..> Competencia : usa
    CompetenciaRepositorio ..> Categoria : usa
    CompetenciaRepositorio ..> Inscripcion : usa
    CompetenciaRepositorio ..> ListaBuenaFe : usa
    UsuarioRepositorio ..> Usuario : usa
    JuegoRepositorio ..> Partido : usa
    JuegoRepositorio ..> JugadorPartido : usa
    JugadorRepositorio ..> Jugador : usa
    JugadorRepositorio ..> JugadorClub : usa

namespace Dominio.Repositorios{
    class ClubRepositorio{
        <<interface>>
        + buscar_por_id_usuario(id_usuario) : list[Club]
        + buscar_por_id(id_club): Club
        + buscar_por_nombre(nombre): list[Club]
        + guardar(nombre)
        + link_user_to_club(idUsuario, idClub, rol)
    }
    class CompetenciaRepositorio{
        <<interface>>
        + guardar_competencia(nombre_competencia, anio, tipo)
        + buscar_competencia_por_id(idCompetencia)
        + obtener_todas_competencias()
        + guardar_categoria(nombre_categoria)
        + obtener_categorias()
        + guardar_inscripcion(idClub, idCategoria, idCompetencia)
        + buscar_inscripcion_por_id(idInscripcion)
        + obtener_inscripciones_por_club(idClub)
        + guardar_lista_buena_fe(fecha, idInscripcion)
        + obtener_lista_por_inscripcion(idInscripcion)
        + agregar_jugador_lista(idJugador, idListaBuenaFe)
        + obtener_jugadores_lista(idListaBuenaFe)
    }
    class UsuarioRepositorio{
        <<interface>>
        + encontrar_por_mail(email)
        + encontrar_por_id(id)
        + guardar(nombre, email, pw)
    }
    class JuegoRepositorio{
        <<interface>>
        + buscar_por_club(id_club)
        + buscar_por_id(idPartido)
        + guardar_partido(partido)
        + guardar_boxscore(boxscore)
    }
    class JugadorRepositorio{
        <<interface>>
        + buscar_por_id(id_jugador)
        + buscar_por_dni(dni_jugador)
        + buscar_por_club(idClub)
        + guardar(nombre, apellido, dni, anioNacimiento)
        + link_to_club(id_jugador, id_club, fechaDesde)
        + club_activo(id_jugador)
    }
}
namespace Dominio.Entidades{
    class Club{
        <<Dataclass>>
        + nombre: str
        + idClub: int
    }
    class UsuarioClub{
        <<Dataclass>>
        + rol : str
        + idUsuario: int
        + idClub: int
    }
    class Competencia{
        <<Dataclass>>
        + nombre
        + anio
        + tipo
        + idCompetencia
    }
    class Categoria{
        <<Dataclass>>
        + nombre
        + idCategoria
    }
    class Inscripcion{
        <<Dataclass>>
        + idClub
        + idCategoria
        + idCompetencia
        + idInscripcion
    }
    class ListaBuenaFe{
        <<Dataclass>>
        + fechaPresentacion
        + idInscripcion
        + idListaBuenaFe
    }
    class Usuario{
        <<Dataclass>>
        + nombre
        + email
        + pw
        + idusuario
    }
    class JugadorPartido{
        <<Dataclass>>
        + idJugador
        + idPartido
        + idClub
        + minutosJugados
        + puntos
        + t2c
        + t2l
        + t3c
        + t3l
        + t1c
        + t1l
        + rebotesDef
        + rebotesOf
        + asistencias
        + recuperos
        + perdidas
        + taponesRecibidos
        + taponesRealizados
        + faltasRecibidas
        + faltasCometidas
    }
    class Partido{
        <<Dataclass>>
        + fecha
        + estadio
        + idCompetencia
        + idClubLocal
        + idClubVisitante
        + idPartido
    }
    class Jugador{
        <<Dataclass>>
        + nombre
        + apellido
        + dni
        + anioNacimiento
        + idJugador
    }
    class JugadorClub{
        <<Dataclass>>
        + fechaDesde
        + fechaHasta
        + idJugador
        + idClub
    }
}
namespace Infraestructura.Repositorios{
    class SqliteClubRepositorio{
        + conexion
    }
    class SqliteJuegoRepositorio{
        + conexion
    }
    class SquliteJugadorRepositorio{
        + conexion
    }
    class SqliteUsuarioRepositorio{
        + conexion
        + _row_to_entity(row)
    }
    class SqliteCompetenciaRepositorio{
        + conexion
        + _row_to_entity(row)
    }
}
namespace Infraestructura.Persistencia{
    class SQLiteManager{
        + db_path
        + schema_path
        + views_path
        + seed_path
        + limpieza_path
        + conexion
        + connect()
        + inicializar_schema()
        + cargar_seed()
        + get_connection()
        + close_connection()
        + limpieza()
    }
}
```

## Diagrama Patron repositorio

```mermaid
flowchart LR
    db[(estadisticas.db)]
    dbManager["SQLiteManager"]
    repoUsuario["SqliteUsuarioRepositorio"]
    repoJugador["SquliteJugadorRepositorio"]
    repoJuego["SqliteJuegoRepositorio"]
    repoClub["SqliteClubRepositorio"]
    repoCompetencias["SQL Repositorio Competencia"]
    U[(USUARIO)]
    C[(CLUB)]
    UC[(USUARIOCLUB)]
    J[(JUGADOR)]
    JC[(JUGADORCLUB)]
    COM[(COMPETENCIA)]
    CAT[(CATEGORIA)]
    I[(INSCRIPCION)]
    LBF[(LISTABUENAFE)]
    JLBF[(JUGADORLISTABUENAFE)]
    P[(PARTIDO)]
    JP[(JUGADORPARTIDO)]

    subgraph conexion
    db-->|"Genera una conexion <br> a la base de datos"|dbManager
    end

    subgraph Repositorios
    dbManager -->|"Conexion Unica"| repoUsuario
    dbManager -->|"Conexion Unica"| repoJugador
    dbManager -->|"Conexion Unica"| repoJuego
    dbManager -->|"Conexion Unica"| repoClub
    dbManager -->|"Conexion Unica"| repoCompetencias
    end

    subgraph EntidadesDB
    repoUsuario -->|"Maneja"|U
    repoClub -->|"Maneja"|C
    repoClub -->|"Maneja"|UC
    repoCompetencias -->|"Maneja"|COM
    repoCompetencias -->|"Maneja"|CAT
    repoCompetencias -->|"Maneja"|I
    repoCompetencias -->|"Maneja"|LBF
    repoCompetencias -->|"Maneja"|JLBF
    repoJuego -->|"Maneja"|P
    repoJuego -->|"Maneja"|JP
    repoJugador -->|"Maneja"|J
    repoJugador -->|"Maneja"|JC
    end
```
