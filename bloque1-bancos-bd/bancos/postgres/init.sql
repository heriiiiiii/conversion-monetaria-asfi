-- =============================================================
-- POSTGRESQL: Bancos FIE (RSA), PYME (ElGamal), Desarrollo (ECC)
-- =============================================================
-- SOLO DDL — Los datos se cargan mediante scripts/populate.sh
-- Nomenclatura de bases de datos:
--   banco_fie                      ← Banco FIE           (RSA)
--   banco_pyme                     ← Banco PYME          (ElGamal)
--   banco_desarrollo_productivo    ← Banco Desarrollo    (ECC)
-- =============================================================

-- ─────────────────────────────────────────
-- BANCO FIE — Cifrado RSA
-- Base de datos: banco_fie
-- ─────────────────────────────────────────
CREATE DATABASE banco_fie
    WITH ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE   = 'en_US.utf8';

\c banco_fie;

CREATE TABLE IF NOT EXISTS cuentas (
    id            SERIAL PRIMARY KEY,
    ci            VARCHAR(512)   NOT NULL,
    nombres       VARCHAR(100)   NOT NULL,
    apellidos     VARCHAR(100)   NOT NULL,
    nro_cuenta    VARCHAR(30)    NOT NULL UNIQUE,
    id_banco      SMALLINT       NOT NULL DEFAULT 11,
    saldo         VARCHAR(512)   NOT NULL DEFAULT '0.00',
    saldo_bs      NUMERIC(18,2)  DEFAULT NULL,
    ci_cifrado    BOOLEAN        NOT NULL DEFAULT FALSE,
    saldo_cifrado BOOLEAN        NOT NULL DEFAULT FALSE,
    code_verif    VARCHAR(512)   DEFAULT NULL,
    created_at    TIMESTAMP      NOT NULL DEFAULT NOW(),
    created_user  VARCHAR(50)    NOT NULL DEFAULT 'system',
    updated_at    TIMESTAMP,
    updated_user  VARCHAR(50),
    deleted_at    TIMESTAMP,
    deleted_user  VARCHAR(50)
);

CREATE INDEX idx_fie_ci          ON cuentas (ci);
CREATE INDEX idx_fie_nro_cuenta  ON cuentas (nro_cuenta);

COMMENT ON TABLE  cuentas            IS 'Banco FIE — Cifrado RSA — DB: banco_fie';
COMMENT ON COLUMN cuentas.id_banco   IS '11 = Banco FIE';
COMMENT ON COLUMN cuentas.saldo      IS 'Saldo USD — puede ser base64(RSA::valor) si saldo_cifrado=TRUE';
COMMENT ON COLUMN cuentas.code_verif IS 'Código de verificación cifrado con RSA';


-- ─────────────────────────────────────────
-- BANCO PYME — Cifrado ElGamal
-- Base de datos: banco_pyme
-- ─────────────────────────────────────────
CREATE DATABASE banco_pyme
    WITH ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE   = 'en_US.utf8';

\c banco_pyme;

CREATE TABLE IF NOT EXISTS cuentas (
    id            SERIAL PRIMARY KEY,
    ci            VARCHAR(512)   NOT NULL,
    nombres       VARCHAR(100)   NOT NULL,
    apellidos     VARCHAR(100)   NOT NULL,
    nro_cuenta    VARCHAR(30)    NOT NULL UNIQUE,
    id_banco      SMALLINT       NOT NULL DEFAULT 12,
    saldo         VARCHAR(512)   NOT NULL DEFAULT '0.00',
    saldo_bs      NUMERIC(18,2)  DEFAULT NULL,
    ci_cifrado    BOOLEAN        NOT NULL DEFAULT FALSE,
    saldo_cifrado BOOLEAN        NOT NULL DEFAULT FALSE,
    code_verif    VARCHAR(512)   DEFAULT NULL,
    created_at    TIMESTAMP      NOT NULL DEFAULT NOW(),
    created_user  VARCHAR(50)    NOT NULL DEFAULT 'system',
    updated_at    TIMESTAMP,
    updated_user  VARCHAR(50),
    deleted_at    TIMESTAMP,
    deleted_user  VARCHAR(50)
);

CREATE INDEX idx_pyme_ci          ON cuentas (ci);
CREATE INDEX idx_pyme_nro_cuenta  ON cuentas (nro_cuenta);

COMMENT ON TABLE  cuentas            IS 'Banco PYME — Cifrado ElGamal — DB: banco_pyme';
COMMENT ON COLUMN cuentas.saldo      IS 'Saldo USD — puede ser base64(ElGamal::valor) si saldo_cifrado=TRUE';
COMMENT ON COLUMN cuentas.code_verif IS 'Código de verificación cifrado con ElGamal';


-- ─────────────────────────────────────────
-- BANCO DE DESARROLLO PRODUCTIVO — Cifrado ECC
-- Base de datos: banco_desarrollo_productivo
-- ─────────────────────────────────────────
CREATE DATABASE banco_desarrollo_productivo
    WITH ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE   = 'en_US.utf8';

\c banco_desarrollo_productivo;

CREATE TABLE IF NOT EXISTS cuentas (
    id            SERIAL PRIMARY KEY,
    ci            VARCHAR(512)   NOT NULL,
    nombres       VARCHAR(100)   NOT NULL,
    apellidos     VARCHAR(100)   NOT NULL,
    nro_cuenta    VARCHAR(30)    NOT NULL UNIQUE,
    id_banco      SMALLINT       NOT NULL DEFAULT 13,
    saldo         VARCHAR(512)   NOT NULL DEFAULT '0.00',
    saldo_bs      NUMERIC(18,2)  DEFAULT NULL,
    ci_cifrado    BOOLEAN        NOT NULL DEFAULT FALSE,
    saldo_cifrado BOOLEAN        NOT NULL DEFAULT FALSE,
    code_verif    VARCHAR(512)   DEFAULT NULL,
    created_at    TIMESTAMP      NOT NULL DEFAULT NOW(),
    created_user  VARCHAR(50)    NOT NULL DEFAULT 'system',
    updated_at    TIMESTAMP,
    updated_user  VARCHAR(50),
    deleted_at    TIMESTAMP,
    deleted_user  VARCHAR(50)
);

CREATE INDEX idx_bdp_ci          ON cuentas (ci);
CREATE INDEX idx_bdp_nro_cuenta  ON cuentas (nro_cuenta);

COMMENT ON TABLE  cuentas            IS 'Banco de Desarrollo Productivo — Cifrado ECC — DB: banco_desarrollo_productivo';
COMMENT ON COLUMN cuentas.saldo      IS 'Saldo USD — puede ser base64(ECC::valor) si saldo_cifrado=TRUE';
COMMENT ON COLUMN cuentas.code_verif IS 'Código de verificación cifrado con ECC';
