-- =============================================================
-- MARIADB: Bancos BISA (Hill), Ganadero (DES),
--          Económico (3DES), Prodem (Blowfish)
-- =============================================================
-- SOLO DDL — Los datos se cargan mediante scripts/populate.sh
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
    ci            VARCHAR(500)   NOT NULL COMMENT 'CI cifrado con Hill (base64)',
    nombres       VARCHAR(100)   NOT NULL,
    apellidos     VARCHAR(100)   NOT NULL,
    nro_cuenta    VARCHAR(30)    NOT NULL,
    id_banco      TINYINT        NOT NULL DEFAULT 5,
    saldo         VARCHAR(500)   NOT NULL DEFAULT '0.00' COMMENT 'Saldo USD, puede ser base64 si saldo_cifrado=1',
    saldo_bs      DECIMAL(18,2)  DEFAULT NULL,
    ci_cifrado    TINYINT(1)     NOT NULL DEFAULT 0,
    saldo_cifrado TINYINT(1)     NOT NULL DEFAULT 0,
    code_verif    VARCHAR(500)   DEFAULT NULL COMMENT 'Código de verificación cifrado con Hill',
    created_at    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_user  VARCHAR(50)    NOT NULL DEFAULT 'system',
    updated_at    DATETIME       ON UPDATE CURRENT_TIMESTAMP,
    updated_user  VARCHAR(50),
    deleted_at    DATETIME,
    deleted_user  VARCHAR(50),
    UNIQUE KEY uq_nro_cuenta (nro_cuenta),
    KEY idx_ci (ci(50))
) ENGINE=InnoDB COMMENT='Banco BISA — Cifrado Hill — DB: banco_bisa';


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
    ci            VARCHAR(500)   NOT NULL COMMENT 'CI cifrado con DES (base64)',
    nombres       VARCHAR(100)   NOT NULL,
    apellidos     VARCHAR(100)   NOT NULL,
    nro_cuenta    VARCHAR(30)    NOT NULL,
    id_banco      TINYINT        NOT NULL DEFAULT 6,
    saldo         VARCHAR(500)   NOT NULL DEFAULT '0.00' COMMENT 'Saldo USD, puede ser base64 si saldo_cifrado=1',
    saldo_bs      DECIMAL(18,2)  DEFAULT NULL,
    ci_cifrado    TINYINT(1)     NOT NULL DEFAULT 0,
    saldo_cifrado TINYINT(1)     NOT NULL DEFAULT 0,
    code_verif    VARCHAR(500)   DEFAULT NULL COMMENT 'Código de verificación cifrado con DES',
    created_at    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_user  VARCHAR(50)    NOT NULL DEFAULT 'system',
    updated_at    DATETIME       ON UPDATE CURRENT_TIMESTAMP,
    updated_user  VARCHAR(50),
    deleted_at    DATETIME,
    deleted_user  VARCHAR(50),
    UNIQUE KEY uq_nro_cuenta (nro_cuenta),
    KEY idx_ci (ci(50))
) ENGINE=InnoDB COMMENT='Banco Ganadero — Cifrado DES — DB: banco_ganadero';


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
    ci            VARCHAR(500)   NOT NULL COMMENT 'CI cifrado con 3DES (base64)',
    nombres       VARCHAR(100)   NOT NULL,
    apellidos     VARCHAR(100)   NOT NULL,
    nro_cuenta    VARCHAR(30)    NOT NULL,
    id_banco      TINYINT        NOT NULL DEFAULT 7,
    saldo         VARCHAR(500)   NOT NULL DEFAULT '0.00' COMMENT 'Saldo USD, puede ser base64 si saldo_cifrado=1',
    saldo_bs      DECIMAL(18,2)  DEFAULT NULL,
    ci_cifrado    TINYINT(1)     NOT NULL DEFAULT 0,
    saldo_cifrado TINYINT(1)     NOT NULL DEFAULT 0,
    code_verif    VARCHAR(500)   DEFAULT NULL COMMENT 'Código de verificación cifrado con 3DES',
    created_at    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_user  VARCHAR(50)    NOT NULL DEFAULT 'system',
    updated_at    DATETIME       ON UPDATE CURRENT_TIMESTAMP,
    updated_user  VARCHAR(50),
    deleted_at    DATETIME,
    deleted_user  VARCHAR(50),
    UNIQUE KEY uq_nro_cuenta (nro_cuenta),
    KEY idx_ci (ci(50))
) ENGINE=InnoDB COMMENT='Banco Económico — Cifrado 3DES — DB: banco_economico';


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
    ci            VARCHAR(500)   NOT NULL COMMENT 'CI cifrado con Blowfish (base64)',
    nombres       VARCHAR(100)   NOT NULL,
    apellidos     VARCHAR(100)   NOT NULL,
    nro_cuenta    VARCHAR(30)    NOT NULL,
    id_banco      TINYINT        NOT NULL DEFAULT 8,
    saldo         VARCHAR(500)   NOT NULL DEFAULT '0.00' COMMENT 'Saldo USD, puede ser base64 si saldo_cifrado=1',
    saldo_bs      DECIMAL(18,2)  DEFAULT NULL,
    ci_cifrado    TINYINT(1)     NOT NULL DEFAULT 0,
    saldo_cifrado TINYINT(1)     NOT NULL DEFAULT 0,
    code_verif    VARCHAR(500)   DEFAULT NULL COMMENT 'Código de verificación cifrado con Blowfish',
    created_at    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_user  VARCHAR(50)    NOT NULL DEFAULT 'system',
    updated_at    DATETIME       ON UPDATE CURRENT_TIMESTAMP,
    updated_user  VARCHAR(50),
    deleted_at    DATETIME,
    deleted_user  VARCHAR(50),
    UNIQUE KEY uq_nro_cuenta (nro_cuenta),
    KEY idx_ci (ci(50))
) ENGINE=InnoDB COMMENT='Banco Prodem — Cifrado Blowfish — DB: banco_prodem';

FLUSH PRIVILEGES;
