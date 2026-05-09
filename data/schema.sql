-- Creacion de esquema de base de datos
create schema if not exists appbasquet;

-- Tabla usuario
CREATE TABLE IF NOT EXISTS usuario (
    idUsuario INT AUTO_INCREMENT NOT NULL,
    nombre VARCHAR(45) NOT NULL,
    email VARCHAR(45) NOT NULL,
    contrasenia VARCHAR(45) NOT NULL,
    PRIMARY KEY (idUsuario)
);

-- Tabla Club
CREATE TABLE IF NOT EXISTS club (
    idCLub INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(45) NOT NULL,
    PRIMARY KEY (idClub)
);

-- Tabla usuarioClub
CREATE TABLE IF NOT EXISTS usuarioClub (
    idUsuario INT NOT NULL,
    idClub INT NOT NULL,
    roEntrenador VARCHAR(50),
    PRIMARY KEY (idUsuario , idClub),
    FOREIGN KEY (idUsuario)
        REFERENCES usuario (idUsuario)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (idClub)
        REFERENCES club (idClub)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabla jugador
CREATE TABLE IF NOT EXISTS jugador (
    idJugador INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(45) NOT NULL,
    apellido VARCHAR(45) NOT NULL,
    dni INT NOT NULL,
    anioNacimiento YEAR,
    PRIMARY KEY (idJugador)
);

-- JugadorClub
CREATE TABLE IF NOT EXISTS jugadorClub (
    idJugador INT NOT NULL,
    idClub INT NOT NULL,
    fechaDesde DATE NOT NULL,
    fechaHasta DATE,
    PRIMARY KEY (idJugador , idClub),
    FOREIGN KEY (idJugador)
        REFERENCES jugador (idJugador)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (idClub)
        REFERENCES club (idClub)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabla competencia
CREATE TABLE IF NOT EXISTS competencia (
    idCompetencia INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(45) NOT NULL,
    anio YEAR NOT NULL,
    tipo VARCHAR(45),
    PRIMARY KEY (idCompetencia)
);

-- Tabla categoria
CREATE TABLE IF NOT EXISTS categoria (
    idCategoria INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(45) NOT NULL,
    PRIMARY KEY (idCompetencia)
);

-- Tabla inscripcion
CREATE TABLE IF NOT EXISTS inscripcion (
    idInscripcion INT NOT NULL AUTO_INCREMENT,
    idClub INT NOT NULL,
    idCategoria INT NOT NULL,
    idCompetencia INT NOT NULL,
    PRIMARY KEY (idInscripcion),
    FOREIGN KEY (idClub)
        REFERENCES club (idClub)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (idCategoria)
        REFERENCES categoria (idCategoria)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (idCompetencia)
        REFERENCES competencia (idCompetencia)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabla Lista de buena Fe
CREATE TABLE IF NOT EXISTS listaBuenaFe (
    idListaBuenaFe INT NOT NULL AUTO_INCREMENT,
    fechaPresentacion DATE NOT NULL,
    idInscripcion INT NOT NULL,
    PRIMARY KEY (idListaBuenaFe),
    FOREIGN KEY (idInscripcion)
        REFERENCES inscripcion (idInscripcion)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabla Jugador Lista Buena Fe
CREATE TABLE IF NOT EXISTS jugadorListaBuenaFe (
    idJugador INT NOT NULL,
    idListaBuenaFe INT NOT NULL,
    PRIMARY KEY (idJugador , idListaBuenaFe),
    FOREIGN KEY (idJugador)
        REFERENCES jugador (idJugador)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (idListaBuenaFe)
        REFERENCES listaBuenaFe (idListaBuenaFe)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabla Partido
CREATE TABLE IF NOT EXISTS partido (
    idPartido INT NOT NULL AUTO_INCREMENT,
    fecha DATE NOT NULL,
    estadio VARCHAR(45) NOT NULL,
    idCompetencia INT NOT NULL,
    idClubLocal INT NOT NULL,
    idClubVisitante INT NOT NULL,
    PRIMARY KEY (idPartido),
    FOREIGN KEY (idCompetencia)
        REFERENCES competencia (idCompetencia)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (idClubLocal)
        REFERENCES club (idClub)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (idClubVisitante)
        REFERENCES club (idClub)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabla jugador Partido
CREATE TABLE IF NOT EXISTS jugadorPartido (
    idJugador INT NOT NULL,
    idPartido INT NOT NULL,
    idClub INT NOT NULL,
    minutosJugados INT NOT NULL,
    puntos INT NOT NULL,
    T2C INT NOT NULL,
    T2L INT NOT NULL,
    T3C INT NOT NULL,
    T3L INT NOT NULL,
    T1C INT NOT NULL,
    T1L INT NOT NULL,
    rebotesDef INT NOT NULL,
    rebotesOf INT NOT NULL,
    asistencias INT NOT NULL,
    recuperos INT NOT NULL,
    perdidas INT NOT NULL,
    taponesRecibidos INT NOT NULL,
    taponesRealizados INT NOT NULL,
    faltasRecibidas INT NOT NULL,
    faltasCometidas INT NOT NULL,
    PRIMARY KEY (idJugador , idPartido),
    FOREIGN KEY (idJugador)
        REFERENCES jugador (idJugador)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    FOREIGN KEY (idPartido)
        REFERENCES partido (idPartido)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    FOREIGN KEY (idClub)
        REFERENCES club (idClub)
        ON DELETE RESTRICT ON UPDATE RESTRICT
);