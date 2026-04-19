CREATE DATABASE IF NOT EXISTS TP2;

CREATE USER IF NOT EXISTS 'prode_user'@'localhost' IDENTIFIED BY 'tu_contraseña_sql';
GRANT ALL PRIVILEGES ON TP2.* TO 'prode_user'@'localhost';
FLUSH PRIVILEGES;
USE TP2;

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL ,
    email VARCHAR(255) NOT NULL UNIQUE    
);

CREATE TABLE IF NOT EXISTS partidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipo_local VARCHAR(255) NOT NULL,
    equipo_visitante VARCHAR(255) NOT NULL,
    fecha DATETIME NOT NULL,
    fase VARCHAR(255) NOT NULL,
    goles_local INT NULL,
    goles_visitante INT NULL
);

CREATE TABLE IF NOT EXISTS predicciones(
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    partido_id INT NOT NULL,
    goles_local INT NOT NULL,
    goles_visitante INT NOT NULL,
    UNIQUE KEY
    uq_usuario_partido (usuario_id, partido_id),
    CONSTRAINT
    fk_predicciones_usuario
    FOREIGN KEY
    (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    CONSTRAINT
    fk_predicciones_partido
    FOREIGN KEY
    (partido_id) REFERENCES partidos(id) ON DELETE CASCADE
);
