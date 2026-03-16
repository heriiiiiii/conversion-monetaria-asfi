-- =============================================================
-- POSTGRESQL: Bancos FIE (RSA), PYME (ElGamal), Desarrollo (ECC)
-- =============================================================
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
    ci            VARCHAR(20)    NOT NULL,
    nombres       VARCHAR(100)   NOT NULL,
    apellidos     VARCHAR(100)   NOT NULL,
    nro_cuenta    VARCHAR(30)    NOT NULL UNIQUE,
    id_banco      SMALLINT       NOT NULL DEFAULT 11,  -- 11 = Banco FIE
    saldo         NUMERIC(18,2)  NOT NULL DEFAULT 0.00,
    code_verif    VARCHAR(255),
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
COMMENT ON COLUMN cuentas.code_verif IS 'Número de cuenta cifrado con RSA';

INSERT INTO cuentas (ci, nombres, apellidos, nro_cuenta, saldo, code_verif, created_user) VALUES
  ('8012345',  'Sofía',    'Mamani Quispe',   'FIE-100001', 15000.00, 'RSA_ENC_001', 'admin'),
  ('7523456',  'Carlos',   'Torrez Vargas',   'FIE-100002', 8500.50,  'RSA_ENC_002', 'admin'),
  ('6034567',  'Ana',      'López Flores',    'FIE-100003', 22300.75, 'RSA_ENC_003', 'admin'),
  ('5145678',  'Miguel',   'Condori Apaza',   'FIE-100004', 3200.00,  'RSA_ENC_004', 'admin'),
  ('9256789',  'Valentina','Rojas Mendoza',   'FIE-100005', 47000.20, 'RSA_ENC_005', 'admin');


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
    ci            VARCHAR(20)    NOT NULL,
    nombres       VARCHAR(100)   NOT NULL,
    apellidos     VARCHAR(100)   NOT NULL,
    nro_cuenta    VARCHAR(30)    NOT NULL UNIQUE,
    id_banco      SMALLINT       NOT NULL DEFAULT 12,  -- 12 = Banco PYME
    saldo         NUMERIC(18,2)  NOT NULL DEFAULT 0.00,
    code_verif    VARCHAR(255),
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
COMMENT ON COLUMN cuentas.code_verif IS 'Número de cuenta cifrado con ElGamal';

INSERT INTO cuentas (ci, nombres, apellidos, nro_cuenta, saldo, code_verif, created_user) VALUES
  ('7011111',  'Roberto',  'Gutiérrez Luna',  'PYME-200001', 9000.00,  'ELGAMAL_ENC_001', 'admin'),
  ('6022222',  'Patricia', 'Salinas Cruz',    'PYME-200002', 14500.00, 'ELGAMAL_ENC_002', 'admin'),
  ('8033333',  'Juan',     'Huanca Mamani',   'PYME-200003', 600.75,   'ELGAMAL_ENC_003', 'admin'),
  ('5044444',  'Isabel',   'Choque Inca',     'PYME-200004', 31200.00, 'ELGAMAL_ENC_004', 'admin'),
  ('9055555',  'Fernando', 'Arce Roca',       'PYME-200005', 5800.50,  'ELGAMAL_ENC_005', 'admin');


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
    ci            VARCHAR(20)    NOT NULL,
    nombres       VARCHAR(100)   NOT NULL,
    apellidos     VARCHAR(100)   NOT NULL,
    nro_cuenta    VARCHAR(30)    NOT NULL UNIQUE,
    id_banco      SMALLINT       NOT NULL DEFAULT 13,  -- 13 = Banco Desarrollo Productivo
    saldo         NUMERIC(18,2)  NOT NULL DEFAULT 0.00,
    code_verif    VARCHAR(255),
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
COMMENT ON COLUMN cuentas.code_verif IS 'Número de cuenta cifrado con ECC';

INSERT INTO cuentas (ci, nombres, apellidos, nro_cuenta, saldo, code_verif, created_user) VALUES
  ('4066666',  'Daniela',  'Poma Quisbert',   'BDP-300001', 120000.00, 'ECC_ENC_001', 'admin'),
  ('7077777',  'Andrés',   'Vega Soria',      'BDP-300002', 85000.50,  'ECC_ENC_002', 'admin'),
  ('6088888',  'Claudia',  'Mercado Ibáñez',  'BDP-300003', 210000.00, 'ECC_ENC_003', 'admin'),
  ('8099999',  'Ernesto',  'Llano Colque',    'BDP-300004', 43000.75,  'ECC_ENC_004', 'admin'),
  ('5100000',  'Mónica',   'Ureña Balcázar',  'BDP-300005', 760000.00, 'ECC_ENC_005', 'admin');
