-- =============================================================
-- MYSQL: Bancos Unión (César), Mercantil SC (Atbash),
--        BNB (Vigenère), BCP (Playfair)
-- =============================================================
-- SOLO DDL — Los datos se cargan mediante scripts/populate.sh
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
    ci            VARCHAR(500)   NOT NULL COMMENT 'CI cifrado con César (base64)',
    nombres       VARCHAR(100)   NOT NULL,
    apellidos     VARCHAR(100)   NOT NULL,
    nro_cuenta    VARCHAR(30)    NOT NULL,
    id_banco      TINYINT        NOT NULL DEFAULT 1,
    saldo         VARCHAR(500)   NOT NULL DEFAULT '0.00' COMMENT 'Saldo USD, puede ser base64 si saldo_cifrado=1',
    saldo_bs      DECIMAL(18,2)  DEFAULT NULL,
    ci_cifrado    TINYINT(1)     NOT NULL DEFAULT 0,
    saldo_cifrado TINYINT(1)     NOT NULL DEFAULT 0,
    code_verif    VARCHAR(500)   DEFAULT NULL COMMENT 'Código de verificación cifrado con César',
    created_at    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_user  VARCHAR(50)    NOT NULL DEFAULT 'system',
    updated_at    DATETIME       ON UPDATE CURRENT_TIMESTAMP,
    updated_user  VARCHAR(50),
    deleted_at    DATETIME,
    deleted_user  VARCHAR(50),
    UNIQUE KEY uq_nro_cuenta (nro_cuenta),
    KEY idx_ci (ci(50))
) ENGINE=InnoDB COMMENT='Banco Unión — Cifrado César — DB: banco_union';


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
    ci            VARCHAR(500)   NOT NULL COMMENT 'CI cifrado con Atbash (base64)',
    nombres       VARCHAR(100)   NOT NULL,
    apellidos     VARCHAR(100)   NOT NULL,
    nro_cuenta    VARCHAR(30)    NOT NULL,
    id_banco      TINYINT        NOT NULL DEFAULT 2,
    saldo         VARCHAR(500)   NOT NULL DEFAULT '0.00' COMMENT 'Saldo USD, puede ser base64 si saldo_cifrado=1',
    saldo_bs      DECIMAL(18,2)  DEFAULT NULL,
    ci_cifrado    TINYINT(1)     NOT NULL DEFAULT 0,
    saldo_cifrado TINYINT(1)     NOT NULL DEFAULT 0,
    code_verif    VARCHAR(500)   DEFAULT NULL COMMENT 'Código de verificación cifrado con Atbash',
    created_at    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_user  VARCHAR(50)    NOT NULL DEFAULT 'system',
    updated_at    DATETIME       ON UPDATE CURRENT_TIMESTAMP,
    updated_user  VARCHAR(50),
    deleted_at    DATETIME,
    deleted_user  VARCHAR(50),
    UNIQUE KEY uq_nro_cuenta (nro_cuenta),
    KEY idx_ci (ci(50))
) ENGINE=InnoDB COMMENT='Banco Mercantil Santa Cruz — Cifrado Atbash — DB: banco_mercantil_santa_cruz';


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
    ci            VARCHAR(500)   NOT NULL COMMENT 'CI cifrado con Vigenère (base64)',
    nombres       VARCHAR(100)   NOT NULL,
    apellidos     VARCHAR(100)   NOT NULL,
    nro_cuenta    VARCHAR(30)    NOT NULL,
    id_banco      TINYINT        NOT NULL DEFAULT 3,
    saldo         VARCHAR(500)   NOT NULL DEFAULT '0.00' COMMENT 'Saldo USD, puede ser base64 si saldo_cifrado=1',
    saldo_bs      DECIMAL(18,2)  DEFAULT NULL,
    ci_cifrado    TINYINT(1)     NOT NULL DEFAULT 0,
    saldo_cifrado TINYINT(1)     NOT NULL DEFAULT 0,
    code_verif    VARCHAR(500)   DEFAULT NULL COMMENT 'Código de verificación cifrado con Vigenère',
    created_at    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_user  VARCHAR(50)    NOT NULL DEFAULT 'system',
    updated_at    DATETIME       ON UPDATE CURRENT_TIMESTAMP,
    updated_user  VARCHAR(50),
    deleted_at    DATETIME,
    deleted_user  VARCHAR(50),
    UNIQUE KEY uq_nro_cuenta (nro_cuenta),
    KEY idx_ci (ci(50))
) ENGINE=InnoDB COMMENT='Banco Nacional de Bolivia (BNB) — Cifrado Vigenère — DB: banco_bnb';


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
    ci            VARCHAR(500)   NOT NULL COMMENT 'CI cifrado con Playfair (base64)',
    nombres       VARCHAR(100)   NOT NULL,
    apellidos     VARCHAR(100)   NOT NULL,
    nro_cuenta    VARCHAR(30)    NOT NULL,
    id_banco      TINYINT        NOT NULL DEFAULT 4,
    saldo         VARCHAR(500)   NOT NULL DEFAULT '0.00' COMMENT 'Saldo USD, puede ser base64 si saldo_cifrado=1',
    saldo_bs      DECIMAL(18,2)  DEFAULT NULL,
    ci_cifrado    TINYINT(1)     NOT NULL DEFAULT 0,
    saldo_cifrado TINYINT(1)     NOT NULL DEFAULT 0,
    code_verif    VARCHAR(500)   DEFAULT NULL COMMENT 'Código de verificación cifrado con Playfair',
    created_at    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_user  VARCHAR(50)    NOT NULL DEFAULT 'system',
    updated_at    DATETIME       ON UPDATE CURRENT_TIMESTAMP,
    updated_user  VARCHAR(50),
    deleted_at    DATETIME,
    deleted_user  VARCHAR(50),
    UNIQUE KEY uq_nro_cuenta (nro_cuenta),
    KEY idx_ci (ci(50))
) ENGINE=InnoDB COMMENT='Banco de Crédito de Bolivia (BCP) — Cifrado Playfair — DB: banco_bcp';

FLUSH PRIVILEGES;
