CREATE DATABASE IF NOT EXISTS db_agenda_turistica;

USE db_agenda_turistica;

CREATE TABLE
  IF NOT EXISTS `usuarios` (
    `id_usuario` INT (10) NOT NULL AUTO_INCREMENT,
    `nombreusuario` VARCHAR(255) NOT NULL,
    `email` VARCHAR(255) NOT NULL,
    `contrasenia` VARCHAR(255) NOT NULL,
    `municipio` VARCHAR(255) NOT NULL,
    `estado` int (1) NOT NULL DEFAULT 0,
    `tipo` int (1) NOT NULL DEFAULT 0,
    PRIMARY KEY (id_usuario)
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE
  IF NOT EXISTS `municipios` (
    `id_municipio` int (11) NOT NULL AUTO_INCREMENT,
    `nombre_municipio` varchar(100) NOT NULL,
    PRIMARY KEY (`id_municipio`)
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

-- CREATE TABLE IF NOT EXISTS `localidad` (
--   `id_localidad` int(11) NOT NULL AUTO_INCREMENT,
--   `nombre_localidad` varchar(100) NOT NULL,
--   PRIMARY KEY (`id_localidad`)
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
CREATE TABLE
  `localidades` (
    `id_localidad` int (11) NOT NULL AUTO_INCREMENT,
    `nombre_localidad` varchar(100) NOT NULL,
    `id_municipio` int (11) NOT NULL,
    PRIMARY KEY (`id_localidad`),
    KEY `id_municipio` (`id_municipio`),
    CONSTRAINT `localidades_ibfk_1` FOREIGN KEY (`id_municipio`) REFERENCES `municipios` (`id_municipio`)
  ) ENGINE = InnoDB AUTO_INCREMENT = 11 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

'2024'
CREATE TABLE
  IF NOT EXISTS `eventos` (
    `id_evento` int (11) NOT NULL AUTO_INCREMENT,
    `nombre_evento` varchar(100) NOT NULL,
    `id_usuario` int (10) NOT NULL,
    `id_municipio` int (10) NOT NULL,
    `id_localidad` int (10) NOT NULL,
    `direccion` varchar(255) DEFAULT NULL,
    `fecha_inicio` date DEFAULT NULL,
    `mes_estimado` varchar(255) DEFAULT NULL,
    `hora` smallint (6) DEFAULT NULL, -- `hora` time DEFAULT NULL,
    `id_tipo_evento` int (10) NOT NULL,
    `descripcion` text DEFAULT NULL,
    `palabras_claves` text DEFAULT NULL,
    `id_estado` int (1) NOT NULL DEFAULT 0,
    PRIMARY KEY (`id_evento`),
    KEY `id_municipio` (`id_municipio`),
    CONSTRAINT `eventos_ibfk_1` FOREIGN KEY (`id_municipio`) REFERENCES `municipios` (`id_municipio`)
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

-- INSERT INTO db_agenda_turistica.municipios
-- ( nombre_municipio)
-- VALUES( "Todos");
-- INSERT INTO db_agenda_turistica.usuarios
-- ( nombreusuario, email, contrasenia, id_municipio, estado, tipo)
-- VALUES('Admin', 'admin@admin.com', '1234', 1, 1, 1);
-- INSERT INTO db_agenda_turistica.municipios
-- ( nombre_municipio)
-- VALUES( '');
-- INSERT INTO db_agenda_turistica.localidades
-- ( nombre_localidad, id_municipio)
-- VALUES( '', 0);
-- INSERT INTO db_agenda_turistica.eventos
-- (nombre_evento, id_usuario, id_municipio, id_localidad, direccion, fecha_inicio, mes_estimado, hora, id_tipo_evento, descripcion, palabras_claves)
-- VALUES('evento prueba', 1, 1, 1, "direccionx 1", '2024-05-01',"Mayo", NULL, 1, "descripcion evento", "Palabras claves");
ALTER TABLE `eventos`
ADD COLUMN `img1` VARCHAR(255) DEFAULT NULL,
ADD COLUMN `img2` VARCHAR(255) DEFAULT NULL,
ADD COLUMN `img3` VARCHAR(255) DEFAULT NULL;