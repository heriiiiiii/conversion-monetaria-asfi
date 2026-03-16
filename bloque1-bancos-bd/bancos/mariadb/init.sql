-- =============================================================
-- MARIADB: Bancos BISA (Hill), Ganadero (DES),
--          Económico (3DES), Prodem (Blowfish)
-- =============================================================
-- Nomenclatura de bases de datos:
--   banco_bisa      ← Banco BISA     (Hill)
--   banco_ganadero  ← Banco Ganadero (DES)
--   banco_economico ← Banco Económico(3DES)
--   banco_prodem    ← Banco Prodem   (Blowfish)
-- =============================================================

CREATE USER IF NOT EXISTS 'admin'@'%' IDENTIFIED BY 'admin123';

-- ─────────────────────────────────────────
-- BANCO BISA — Cifrado Hill
-- Base de datos: banco_bisa
-- ─────────────────────────────────────────
CREATE DATABASE IF NOT EXISTS banco_bisa
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

GRANT ALL PRIVILEGES ON banco_bisa.* TO 'admin'@'%';

USE banco_bisa;

CREATE TABLE IF NOT EXISTS cuentas (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    ci            VARCHAR(20)    NOT NULL,
    nombres       VARCHAR(100)   NOT NULL,
    apellidos     VARCHAR(100)   NOT NULL,
    nro_cuenta    VARCHAR(30)    NOT NULL,
    id_banco      TINYINT        NOT NULL DEFAULT 5,   -- 5 = Banco BISA
    saldo         DECIMAL(18,2)  NOT NULL DEFAULT 0.00,
    code_verif    VARCHAR(255)   COMMENT 'Número de cuenta cifrado con Hill',
    created_at    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_user  VARCHAR(50)    NOT NULL DEFAULT 'system',
    updated_at    DATETIME       ON UPDATE CURRENT_TIMESTAMP,
    updated_user  VARCHAR(50),
    deleted_at    DATETIME,
    deleted_user  VARCHAR(50),
    UNIQUE KEY uq_nro_cuenta (nro_cuenta),
    KEY idx_ci (ci)
) ENGINE=InnoDB COMMENT='Banco BISA — Cifrado Hill — DB: banco_bisa';

INSERT INTO cuentas (ci, nombres, apellidos, nro_cuenta, saldo, code_verif, created_user) VALUES
  ('5678901', 'Diego',    'Alcón Roca',      'BISA-000001', 17200.00, 'HILL_ENC_001', 'admin'),
  ('6789011', 'Ximena',   'Barrios Colque',  'BISA-000002', 6500.75,  'HILL_ENC_002', 'admin'),
  ('7890121', 'Yolanda',  'Camacho Inca',    'BISA-000003', 39800.50, 'HILL_ENC_003', 'admin'),
  ('8901231', 'Zeinaldy', 'Durán Jiménez',   'BISA-000004', 2100.00,  'HILL_ENC_004', 'admin'),
  ('9012341', 'Alfredo',  'Espinoza Flores', 'BISA-000005', 84300.25, 'HILL_ENC_005', 'admin');


-- ─────────────────────────────────────────
-- BANCO GANADERO — Cifrado DES
-- Base de datos: banco_ganadero
-- ─────────────────────────────────────────
CREATE DATABASE IF NOT EXISTS banco_ganadero
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

GRANT ALL PRIVILEGES ON banco_ganadero.* TO 'admin'@'%';

USE banco_ganadero;

CREATE TABLE IF NOT EXISTS cuentas (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    ci            VARCHAR(20)    NOT NULL,
    nombres       VARCHAR(100)   NOT NULL,
    apellidos     VARCHAR(100)   NOT NULL,
    nro_cuenta    VARCHAR(30)    NOT NULL,
    id_banco      TINYINT        NOT NULL DEFAULT 6,   -- 6 = Banco Ganadero
    saldo         DECIMAL(18,2)  NOT NULL DEFAULT 0.00,
    code_verif    VARCHAR(255)   COMMENT 'Número de cuenta cifrado con DES',
    created_at    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_user  VARCHAR(50)    NOT NULL DEFAULT 'system',
    updated_at    DATETIME       ON UPDATE CURRENT_TIMESTAMP,
    updated_user  VARCHAR(50),
    deleted_at    DATETIME,
    deleted_user  VARCHAR(50),
    UNIQUE KEY uq_nro_cuenta (nro_cuenta),
    KEY idx_ci (ci)
) ENGINE=InnoDB COMMENT='Banco Ganadero — Cifrado DES — DB: banco_ganadero';

INSERT INTO cuentas (ci, nombres, apellidos, nro_cuenta, saldo, code_verif, created_user) VALUES
  ('6789012', 'Elena',    'Soria Cruz',      'GAN-000001', 54000.00, 'DES_ENC_001', 'admin'),
  ('7890122', 'Felipe',   'Torrez Mamani',   'GAN-000002', 8900.50,  'DES_ENC_002', 'admin'),
  ('8901232', 'Gonzalo',  'Ureña Salinas',   'GAN-000003', 23600.75, 'DES_ENC_003', 'admin'),
  ('9012342', 'Hilda',    'Vaca Morales',    'GAN-000004', 1500.00,  'DES_ENC_004', 'admin'),
  ('1023452', 'Ignacio',  'Poma Vargas',     'GAN-000005', 107000.00,'DES_ENC_005', 'admin');


-- ─────────────────────────────────────────
-- BANCO ECONÓMICO — Cifrado 3DES
-- Base de datos: banco_economico
-- ─────────────────────────────────────────
CREATE DATABASE IF NOT EXISTS banco_economico
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

GRANT ALL PRIVILEGES ON banco_economico.* TO 'admin'@'%';

USE banco_economico;

CREATE TABLE IF NOT EXISTS cuentas (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    ci            VARCHAR(20)    NOT NULL,
    nombres       VARCHAR(100)   NOT NULL,
    apellidos     VARCHAR(100)   NOT NULL,
    nro_cuenta    VARCHAR(30)    NOT NULL,
    id_banco      TINYINT        NOT NULL DEFAULT 7,   -- 7 = Banco Económico
    saldo         DECIMAL(18,2)  NOT NULL DEFAULT 0.00,
    code_verif    VARCHAR(255)   COMMENT 'Número de cuenta cifrado con 3DES',
    created_at    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_user  VARCHAR(50)    NOT NULL DEFAULT 'system',
    updated_at    DATETIME       ON UPDATE CURRENT_TIMESTAMP,
    updated_user  VARCHAR(50),
    deleted_at    DATETIME,
    deleted_user  VARCHAR(50),
    UNIQUE KEY uq_nro_cuenta (nro_cuenta),
    KEY idx_ci (ci)
) ENGINE=InnoDB COMMENT='Banco Económico — Cifrado 3DES — DB: banco_economico';

INSERT INTO cuentas (ci, nombres, apellidos, nro_cuenta, saldo, code_verif, created_user) VALUES
  ('7890123', 'Marco',    'López Ibáñez',    'ECO-000001', 11400.00, '3DES_ENC_001', 'admin'),
  ('8901233', 'Natalia',  'Mercado García',  'ECO-000002', 63000.75, '3DES_ENC_002', 'admin'),
  ('9012343', 'Omar',     'Nava Roca',       'ECO-000003', 4200.50,  '3DES_ENC_003', 'admin'),
  ('1023453', 'Pamela',   'Orellana Cruz',   'ECO-000004', 28500.00, '3DES_ENC_004', 'admin'),
  ('2134563', 'Quirino',  'Palacios Inca',   'ECO-000005', 951000.00,'3DES_ENC_005', 'admin');


-- ─────────────────────────────────────────
-- BANCO PRODEM — Cifrado Blowfish
-- Base de datos: banco_prodem
-- ─────────────────────────────────────────
CREATE DATABASE IF NOT EXISTS banco_prodem
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

GRANT ALL PRIVILEGES ON banco_prodem.* TO 'admin'@'%';

USE banco_prodem;

CREATE TABLE IF NOT EXISTS cuentas (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    ci            VARCHAR(20)    NOT NULL,
    nombres       VARCHAR(100)   NOT NULL,
    apellidos     VARCHAR(100)   NOT NULL,
    nro_cuenta    VARCHAR(30)    NOT NULL,
    id_banco      TINYINT        NOT NULL DEFAULT 8,   -- 8 = Banco Prodem
    saldo         DECIMAL(18,2)  NOT NULL DEFAULT 0.00,
    code_verif    VARCHAR(255)   COMMENT 'Número de cuenta cifrado con Blowfish',
    created_at    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_user  VARCHAR(50)    NOT NULL DEFAULT 'system',
    updated_at    DATETIME       ON UPDATE CURRENT_TIMESTAMP,
    updated_user  VARCHAR(50),
    deleted_at    DATETIME,
    deleted_user  VARCHAR(50),
    UNIQUE KEY uq_nro_cuenta (nro_cuenta),
    KEY idx_ci (ci)
) ENGINE=InnoDB COMMENT='Banco Prodem — Cifrado Blowfish — DB: banco_prodem';

INSERT INTO cuentas (ci, nombres, apellidos, nro_cuenta, saldo, code_verif, created_user) VALUES
  ('8901234', 'Laura',    'Choque Vargas',   'PROD-000001', 6800.00,  'BLOWFISH_ENC_001', 'admin'),
  ('9012344', 'Sebastián','Rivera Mamani',   'PROD-000002', 14300.50, 'BLOWFISH_ENC_002', 'admin'),
  ('1023454', 'Teresa',   'Salinas Quispe',  'PROD-000003', 2900.75,  'BLOWFISH_ENC_003', 'admin'),
  ('2134564', 'Ulises',   'Torrez Roca',     'PROD-000004', 47000.00, 'BLOWFISH_ENC_004', 'admin'),
  ('3245674', 'Valeria',  'Ureña Flores',    'PROD-000005', 19200.25, 'BLOWFISH_ENC_005', 'admin');

FLUSH PRIVILEGES;
