-- =============================================================
-- MYSQL: Bancos Unión (César), Mercantil SC (Atbash),
--        BNB (Vigenère), BCP (Playfair)
-- =============================================================
-- Nomenclatura de bases de datos:
--   banco_union                ← Banco Unión                     (César)
--   banco_mercantil_santa_cruz ← Banco Mercantil Santa Cruz      (Atbash)
--   banco_bnb                  ← Banco Nacional de Bolivia BNB   (Vigenère)
--   banco_bcp                  ← Banco de Crédito de Bolivia BCP (Playfair)
-- =============================================================

CREATE USER IF NOT EXISTS 'admin'@'%' IDENTIFIED BY 'admin123';

-- ─────────────────────────────────────────
-- BANCO UNIÓN — Cifrado César
-- Base de datos: banco_union
-- ─────────────────────────────────────────
CREATE DATABASE IF NOT EXISTS banco_union
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

GRANT ALL PRIVILEGES ON banco_union.* TO 'admin'@'%';

USE banco_union;

CREATE TABLE IF NOT EXISTS cuentas (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    ci            VARCHAR(20)    NOT NULL,
    nombres       VARCHAR(100)   NOT NULL,
    apellidos     VARCHAR(100)   NOT NULL,
    nro_cuenta    VARCHAR(30)    NOT NULL,
    id_banco      TINYINT        NOT NULL DEFAULT 1,   -- 1 = Banco Unión
    saldo         DECIMAL(18,2)  NOT NULL DEFAULT 0.00,
    code_verif    VARCHAR(255)   COMMENT 'Número de cuenta cifrado con César',
    created_at    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_user  VARCHAR(50)    NOT NULL DEFAULT 'system',
    updated_at    DATETIME       ON UPDATE CURRENT_TIMESTAMP,
    updated_user  VARCHAR(50),
    deleted_at    DATETIME,
    deleted_user  VARCHAR(50),
    UNIQUE KEY uq_nro_cuenta (nro_cuenta),
    KEY idx_ci (ci)
) ENGINE=InnoDB COMMENT='Banco Unión — Cifrado César — DB: banco_union';

INSERT INTO cuentas (ci, nombres, apellidos, nro_cuenta, saldo, code_verif, created_user) VALUES
  ('1234567', 'Luis',     'Quispe Mamani',   'UNI-000001', 5200.00,  'CESAR_ENC_001', 'admin'),
  ('2345677', 'María',    'Ríos Torrez',     'UNI-000002', 13400.50, 'CESAR_ENC_002', 'admin'),
  ('3456787', 'Jorge',    'Alarcón Poma',    'UNI-000003', 800.75,   'CESAR_ENC_003', 'admin'),
  ('4567897', 'Elena',    'Mamani Choque',   'UNI-000004', 29100.00, 'CESAR_ENC_004', 'admin'),
  ('5678907', 'Raúl',     'Vega Carrasco',   'UNI-000005', 7650.30,  'CESAR_ENC_005', 'admin');


-- ─────────────────────────────────────────
-- BANCO MERCANTIL SANTA CRUZ — Cifrado Atbash
-- Base de datos: banco_mercantil_santa_cruz
-- ─────────────────────────────────────────
CREATE DATABASE IF NOT EXISTS banco_mercantil_santa_cruz
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

GRANT ALL PRIVILEGES ON banco_mercantil_santa_cruz.* TO 'admin'@'%';

USE banco_mercantil_santa_cruz;

CREATE TABLE IF NOT EXISTS cuentas (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    ci            VARCHAR(20)    NOT NULL,
    nombres       VARCHAR(100)   NOT NULL,
    apellidos     VARCHAR(100)   NOT NULL,
    nro_cuenta    VARCHAR(30)    NOT NULL,
    id_banco      TINYINT        NOT NULL DEFAULT 2,   -- 2 = Banco Mercantil Santa Cruz
    saldo         DECIMAL(18,2)  NOT NULL DEFAULT 0.00,
    code_verif    VARCHAR(255)   COMMENT 'Número de cuenta cifrado con Atbash',
    created_at    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_user  VARCHAR(50)    NOT NULL DEFAULT 'system',
    updated_at    DATETIME       ON UPDATE CURRENT_TIMESTAMP,
    updated_user  VARCHAR(50),
    deleted_at    DATETIME,
    deleted_user  VARCHAR(50),
    UNIQUE KEY uq_nro_cuenta (nro_cuenta),
    KEY idx_ci (ci)
) ENGINE=InnoDB COMMENT='Banco Mercantil Santa Cruz — Cifrado Atbash — DB: banco_mercantil_santa_cruz';

INSERT INTO cuentas (ci, nombres, apellidos, nro_cuenta, saldo, code_verif, created_user) VALUES
  ('2345678', 'María',    'Flores García',   'MSC-000001', 18500.00, 'ATBASH_ENC_001', 'admin'),
  ('3456788', 'Andrés',   'Heredia Loza',    'MSC-000002', 42000.00, 'ATBASH_ENC_002', 'admin'),
  ('4567898', 'Carmen',   'Ibáñez Soria',    'MSC-000003', 7100.25,  'ATBASH_ENC_003', 'admin'),
  ('5678908', 'David',    'Jiménez Alcón',   'MSC-000004', 3300.80,  'ATBASH_ENC_004', 'admin'),
  ('6789018', 'Karina',   'Lima Medina',     'MSC-000005', 55000.00, 'ATBASH_ENC_005', 'admin');


-- ─────────────────────────────────────────
-- BANCO NACIONAL DE BOLIVIA (BNB) — Cifrado Vigenère
-- Base de datos: banco_bnb
-- ─────────────────────────────────────────
CREATE DATABASE IF NOT EXISTS banco_bnb
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

GRANT ALL PRIVILEGES ON banco_bnb.* TO 'admin'@'%';

USE banco_bnb;

CREATE TABLE IF NOT EXISTS cuentas (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    ci            VARCHAR(20)    NOT NULL,
    nombres       VARCHAR(100)   NOT NULL,
    apellidos     VARCHAR(100)   NOT NULL,
    nro_cuenta    VARCHAR(30)    NOT NULL,
    id_banco      TINYINT        NOT NULL DEFAULT 3,   -- 3 = Banco Nacional de Bolivia (BNB)
    saldo         DECIMAL(18,2)  NOT NULL DEFAULT 0.00,
    code_verif    VARCHAR(255)   COMMENT 'Número de cuenta cifrado con Vigenère',
    created_at    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_user  VARCHAR(50)    NOT NULL DEFAULT 'system',
    updated_at    DATETIME       ON UPDATE CURRENT_TIMESTAMP,
    updated_user  VARCHAR(50),
    deleted_at    DATETIME,
    deleted_user  VARCHAR(50),
    UNIQUE KEY uq_nro_cuenta (nro_cuenta),
    KEY idx_ci (ci)
) ENGINE=InnoDB COMMENT='Banco Nacional de Bolivia (BNB) — Cifrado Vigenère — DB: banco_bnb';

INSERT INTO cuentas (ci, nombres, apellidos, nro_cuenta, saldo, code_verif, created_user) VALUES
  ('3456789', 'Pedro',    'Zarate Morales',  'BNB-000001', 9600.00,  'VIGENERE_ENC_001', 'admin'),
  ('4567899', 'Susana',   'Nava Salinas',    'BNB-000002', 23000.75, 'VIGENERE_ENC_002', 'admin'),
  ('5678909', 'Oscar',    'Oporto Vargas',   'BNB-000003', 5500.00,  'VIGENERE_ENC_003', 'admin'),
  ('6789019', 'Patricia', 'Quispe Rojas',    'BNB-000004', 71200.50, 'VIGENERE_ENC_004', 'admin'),
  ('7890129', 'Ricardo',  'Reyes Condori',   'BNB-000005', 18900.00, 'VIGENERE_ENC_005', 'admin');


-- ─────────────────────────────────────────
-- BANCO DE CRÉDITO DE BOLIVIA (BCP) — Cifrado Playfair
-- Base de datos: banco_bcp
-- ─────────────────────────────────────────
CREATE DATABASE IF NOT EXISTS banco_bcp
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

GRANT ALL PRIVILEGES ON banco_bcp.* TO 'admin'@'%';

USE banco_bcp;

CREATE TABLE IF NOT EXISTS cuentas (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    ci            VARCHAR(20)    NOT NULL,
    nombres       VARCHAR(100)   NOT NULL,
    apellidos     VARCHAR(100)   NOT NULL,
    nro_cuenta    VARCHAR(30)    NOT NULL,
    id_banco      TINYINT        NOT NULL DEFAULT 4,   -- 4 = Banco de Crédito de Bolivia (BCP)
    saldo         DECIMAL(18,2)  NOT NULL DEFAULT 0.00,
    code_verif    VARCHAR(255)   COMMENT 'Número de cuenta cifrado con Playfair',
    created_at    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_user  VARCHAR(50)    NOT NULL DEFAULT 'system',
    updated_at    DATETIME       ON UPDATE CURRENT_TIMESTAMP,
    updated_user  VARCHAR(50),
    deleted_at    DATETIME,
    deleted_user  VARCHAR(50),
    UNIQUE KEY uq_nro_cuenta (nro_cuenta),
    KEY idx_ci (ci)
) ENGINE=InnoDB COMMENT='Banco de Crédito de Bolivia (BCP) — Cifrado Playfair — DB: banco_bcp';

INSERT INTO cuentas (ci, nombres, apellidos, nro_cuenta, saldo, code_verif, created_user) VALUES
  ('4567890', 'Rosa',     'Lima Huanca',     'BCP-000001', 32000.00, 'PLAYFAIR_ENC_001', 'admin'),
  ('5678900', 'Tomás',    'Mamani Aguirre',  'BCP-000002', 4800.50,  'PLAYFAIR_ENC_002', 'admin'),
  ('6789010', 'Ursula',   'Nogales Barriga', 'BCP-000003', 88000.00, 'PLAYFAIR_ENC_003', 'admin'),
  ('7890120', 'Víctor',   'Orellana López',  'BCP-000004', 12500.75, 'PLAYFAIR_ENC_004', 'admin'),
  ('8901230', 'Wendy',    'Pinto Alcázar',   'BCP-000005', 6700.00,  'PLAYFAIR_ENC_005', 'admin');

FLUSH PRIVILEGES;
