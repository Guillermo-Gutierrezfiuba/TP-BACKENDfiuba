DROP TABLE IF EXISTS TP2.partidos;
CREATE TABLE IF NOT EXISTS TP2.partidos (
    `id` INT NOT NULL AUTO_INCREMENT,
    `equipo_visitante` VARCHAR(255) NULL,
    `equipo_local` VARCHAR(255) NULL,
    `estadio`VARCHAR(255) NOT NULL,
    `ciudad` VARCHAR(255) NOT NULL,
    `fecha` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `fase_del_torneo` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`id`)
);
SELECT * FROM TP2.partidos