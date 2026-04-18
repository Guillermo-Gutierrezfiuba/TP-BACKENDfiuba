CREATE DATABASE IF NOT EXISTS TP2;
USE TP2;
DROP TABLE IF EXISTS usuarios_apuestas;
CREATE TABLE IF NOT EXISTS usuarios_apuestas(
	`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `usuario` VARCHAR(255),
    `email` VARCHAR(255),
    `prediccion_equip_visit` INT,
    `prediccion_equip_local` INT, 
    `prediccion_final` VARCHAR(255),
    `puntos` INT
);
SELECT * FROM usuarios_apuestas;