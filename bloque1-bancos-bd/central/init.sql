-- =============================================================
-- BASE DE DATOS CENTRAL — PostgreSQL
-- =============================================================
-- Consolida información de todos los bancos del sistema.
-- Tablas: bancos, cuentas_global, transacciones
-- =============================================================

-- ─────────────────────────────────────────
-- TABLA: bancos
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bancos (
    id         SERIAL PRIMARY KEY,
    nombre     VARCHAR(150) NOT NULL UNIQUE,
    algoritmo  VARCHAR(50)  NOT NULL
);

COMMENT ON TABLE  bancos           IS 'Catálogo de todos los bancos del sistema';
COMMENT ON COLUMN bancos.algoritmo IS 'Algoritmo de cifrado usado por el banco';

-- Registro de los 14 bancos con sus algoritmos
INSERT INTO bancos (nombre, algoritmo) VALUES
  ('Banco Unión',                         'César'),
  ('Banco Mercantil Santa Cruz',           'Atbash'),
  ('Banco Nacional de Bolivia (BNB)',      'Vigenère'),
  ('Banco de Crédito de Bolivia (BCP)',    'Playfair'),
  ('Banco BISA',                           'Hill'),
  ('Banco Ganadero',                       'DES'),
  ('Banco Económico',                      '3DES'),
  ('Banco Prodem',                         'Blowfish'),
  ('Banco Solidario',                      'Twofish'),
  ('Banco Fortaleza',                      'AES'),
  ('Banco FIE',                            'RSA'),
  ('Banco PYME',                           'ElGamal'),
  ('Banco de Desarrollo Productivo',       'ECC'),
  ('Banco Nación Argentina',               'ChaCha20');

-- ─────────────────────────────────────────
-- TABLA: cuentas_global
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS cuentas_global (
    id                   SERIAL PRIMARY KEY,
    ci                   VARCHAR(20)  NOT NULL,
    nombres              VARCHAR(100) NOT NULL,
    apellidos            VARCHAR(100) NOT NULL,
    id_banco             INTEGER      NOT NULL REFERENCES bancos(id),
    nro_cuenta_encriptado VARCHAR(500) NOT NULL,
    CONSTRAINT uq_cuenta_banco UNIQUE (ci, id_banco)
);

COMMENT ON TABLE  cuentas_global                      IS 'Vista consolidada de cuentas de todos los bancos';
COMMENT ON COLUMN cuentas_global.nro_cuenta_encriptado IS 'Número de cuenta cifrado con el algoritmo del banco';

CREATE INDEX idx_cg_ci       ON cuentas_global (ci);
CREATE INDEX idx_cg_id_banco ON cuentas_global (id_banco);

-- ─────────────────────────────────────────
-- TABLA: transacciones
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS transacciones (
    id              BIGSERIAL PRIMARY KEY,
    cuenta_origen   VARCHAR(30)    NOT NULL,
    cuenta_destino  VARCHAR(30)    NOT NULL,
    monto           NUMERIC(18,2)  NOT NULL CHECK (monto > 0),
    fecha           TIMESTAMP      NOT NULL DEFAULT NOW(),
    estado          VARCHAR(20)    NOT NULL DEFAULT 'COMPLETADA'
                        CHECK (estado IN ('PENDIENTE', 'COMPLETADA', 'RECHAZADA', 'REVERTIDA')),
    descripcion     VARCHAR(255)
);

COMMENT ON TABLE transacciones IS 'Registro global de transferencias interbancarias e intrabancarias';

CREATE INDEX idx_tx_origen  ON transacciones (cuenta_origen);
CREATE INDEX idx_tx_destino ON transacciones (cuenta_destino);
CREATE INDEX idx_tx_fecha   ON transacciones (fecha DESC);

-- ─────────────────────────────────────────
-- DATOS DE EJEMPLO: cuentas_global
-- ─────────────────────────────────────────
INSERT INTO cuentas_global (ci, nombres, apellidos, id_banco, nro_cuenta_encriptado) VALUES
  -- PostgreSQL banks
  ('8012345',  'Sofía',    'Mamani Quispe',   11, 'UldJLVJTQV9FTkNfMDAx'),  -- FIE RSA
  ('7523456',  'Carlos',   'Torrez Vargas',   11, 'UldJLVJTQV9FTkNfMDAy'),
  ('7011111',  'Roberto',  'Gutiérrez Luna',  12, 'UELZTUV8RVJHTF9FTkNfMDAx'), -- PYME ElGamal
  ('4066666',  'Daniela',  'Poma Quisbert',   13, 'RUNDS1RQRV9FTkNfMDAx'),  -- BDP ECC
  -- MySQL banks
  ('1234567',  'Luis',     'Quispe Mamani',   1,  'Nwhv'),                  -- Unión César
  ('2345678',  'María',    'Flores García',   2,  'Nzirh'),                 -- Mercantil Atbash
  ('3456789',  'Pedro',    'Zarate Morales',  3,  'Bnp-vigenere'),          -- BNB Vigenère
  ('4567890',  'Rosa',     'Lima Huanca',     4,  'PLY-playfair'),          -- BCP Playfair
  -- MariaDB banks
  ('5678901',  'Diego',    'Alcón Roca',      5,  'HLL-hill'),              -- BISA Hill
  ('6789012',  'Elena',    'Soria Cruz',      6,  'DES-ganadero'),          -- Ganadero DES
  ('7890123',  'Marco',    'López Ibáñez',    7,  '3DES-economico'),        -- Económico 3DES
  ('8901234',  'Laura',    'Choque Vargas',   8,  'BLF-prodem'),            -- Prodem Blowfish
  -- MongoDB banks
  ('9012345',  'Paola',    'Mamani Torres',   9,  'TWO-solidario'),         -- Solidario Twofish
  ('1123456',  'Jhon',     'Camacho Pinto',   10, 'AES-fortaleza'),         -- Fortaleza AES
  -- Redis bank
  ('2234567',  'Gabriela', 'Núñez Carrasco',  14, 'CHA-nacion');            -- Nación ChaCha20

-- ─────────────────────────────────────────
-- DATOS DE EJEMPLO: transacciones
-- ─────────────────────────────────────────
INSERT INTO transacciones (cuenta_origen, cuenta_destino, monto, fecha, estado, descripcion) VALUES
  ('FIE-100001',  'PYME-200001',  5000.00, NOW() - INTERVAL '5 days',  'COMPLETADA', 'Transferencia interbancaria FIE → PYME'),
  ('UNI-000001',  'BNB-000001',   1200.50, NOW() - INTERVAL '3 days',  'COMPLETADA', 'Pago de servicios Unión → BNB'),
  ('BCP-000001',  'FIE-100002',    800.00, NOW() - INTERVAL '2 days',  'COMPLETADA', 'Pago proveedor BCP → FIE'),
  ('BDP-300001',  'BISA-000001', 15000.00, NOW() - INTERVAL '1 day',   'COMPLETADA', 'Crédito productivo BDP → BISA'),
  ('PYME-200002', 'BDP-300002',   3500.75, NOW() - INTERVAL '12 hours','COMPLETADA', 'Inversión PYME → BDP'),
  ('SOLD-000001', 'FORT-000001',   250.00, NOW() - INTERVAL '6 hours', 'COMPLETADA', 'Transferencia Solidario → Fortaleza'),
  ('UNI-000002',  'NACIARG-0001', 7800.00, NOW() - INTERVAL '2 hours', 'PENDIENTE',  'Remesa internacional Unión → Nación Argentina'),
  ('FIE-100003',  'FIE-100004',   2000.00, NOW() - INTERVAL '1 hour',  'COMPLETADA', 'Transferencia interna FIE'),
  ('ECO-000001',  'PROD-000001',   450.00, NOW() - INTERVAL '30 mins', 'COMPLETADA', 'Pago cuota Económico → Prodem'),
  ('BNB-000002',  'BCP-000002',   9999.99, NOW(),                       'PENDIENTE',  'Fondeo interbancario BNB → BCP');
