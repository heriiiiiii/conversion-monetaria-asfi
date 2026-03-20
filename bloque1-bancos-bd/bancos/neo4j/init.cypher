// =============================================================
// BANCO NEO4J — Base de Grafos
// Bloque 1, Tarea 9
// =============================================================
// Modelo:
//   (:Cliente {ci, nombres, apellidos})
//   (:Cuenta  {nro_cuenta, id_banco, saldo, ci_cifrado, saldo_cifrado})
//   (:Banco   {id, nombre, algoritmo, motor})
//   (Cliente)-[:TIENE_CUENTA]->(Cuenta)
//   (Cuenta)-[:PERTENECE_A]->(Banco)
// Dataset: 70 registros — 5 por banco (bancos 1–14)
// =============================================================

// ── Limpiar datos previos ─────────────────────────────────────────────────────
MATCH (n) DETACH DELETE n;

// ── Crear nodos Banco ──────────────────────────────────────────────────────────
CREATE (:Banco {id: 1,  nombre: 'Banco Unión',                       algoritmo: 'César',    motor: 'MySQL'});
CREATE (:Banco {id: 2,  nombre: 'Banco Mercantil Santa Cruz',         algoritmo: 'Atbash',   motor: 'MySQL'});
CREATE (:Banco {id: 3,  nombre: 'Banco Nacional de Bolivia (BNB)',    algoritmo: 'Vigenère', motor: 'MySQL'});
CREATE (:Banco {id: 4,  nombre: 'Banco de Crédito de Bolivia (BCP)', algoritmo: 'Playfair', motor: 'MySQL'});
CREATE (:Banco {id: 5,  nombre: 'Banco BISA',                         algoritmo: 'Hill',     motor: 'MariaDB'});
CREATE (:Banco {id: 6,  nombre: 'Banco Ganadero',                     algoritmo: 'DES',      motor: 'MariaDB'});
CREATE (:Banco {id: 7,  nombre: 'Banco Económico',                    algoritmo: '3DES',     motor: 'MariaDB'});
CREATE (:Banco {id: 8,  nombre: 'Banco Prodem',                       algoritmo: 'Blowfish', motor: 'MariaDB'});
CREATE (:Banco {id: 9,  nombre: 'Banco Solidario',                    algoritmo: 'Twofish',  motor: 'MongoDB'});
CREATE (:Banco {id: 10, nombre: 'Banco Fortaleza',                    algoritmo: 'AES',      motor: 'MongoDB'});
CREATE (:Banco {id: 11, nombre: 'Banco FIE',                          algoritmo: 'RSA',      motor: 'PostgreSQL'});
CREATE (:Banco {id: 12, nombre: 'Banco PYME',                         algoritmo: 'ElGamal',  motor: 'PostgreSQL'});
CREATE (:Banco {id: 13, nombre: 'Banco de Desarrollo Productivo',     algoritmo: 'ECC',      motor: 'PostgreSQL'});
CREATE (:Banco {id: 14, nombre: 'Banco Nación Argentina',             algoritmo: 'ChaCha20', motor: 'Redis'});

// ── Índices ───────────────────────────────────────────────────────────────────
CREATE INDEX cliente_ci IF NOT EXISTS FOR (c:Cliente) ON (c.ci);
CREATE INDEX cuenta_nro IF NOT EXISTS FOR (ct:Cuenta)  ON (ct.nro_cuenta);
CREATE INDEX banco_id   IF NOT EXISTS FOR (b:Banco)    ON (b.id);

// ── Banco 1 — Unión (César / MySQL) — 5 cuentas ───────────────────────────────
MATCH (b:Banco {id: 1}) WITH b
CREATE (c1:Cliente {ci: '7100001', nombres: 'María José',    apellidos: 'Mamani Inca'}),
       (ct1:Cuenta {nro_cuenta: 'UNI-000001', id_banco: 1, saldo: 5200.00,    saldo_cifrado: false, ci_cifrado: true}),
       (c1)-[:TIENE_CUENTA]->(ct1), (ct1)-[:PERTENECE_A]->(b)
CREATE (c2:Cliente {ci: '7200001', nombres: 'Pedro Antonio', apellidos: 'Torrez Vargas'}),
       (ct2:Cuenta {nro_cuenta: 'UNI-000002', id_banco: 1, saldo: 13400.50,   saldo_cifrado: false, ci_cifrado: true}),
       (c2)-[:TIENE_CUENTA]->(ct2), (ct2)-[:PERTENECE_A]->(b)
CREATE (c3:Cliente {ci: '7300001', nombres: 'Carmen Lucía',  apellidos: 'Flores García'}),
       (ct3:Cuenta {nro_cuenta: 'UNI-000003', id_banco: 1, saldo: 800.75,     saldo_cifrado: false, ci_cifrado: true}),
       (c3)-[:TIENE_CUENTA]->(ct3), (ct3)-[:PERTENECE_A]->(b)
CREATE (c4:Cliente {ci: '7400001', nombres: 'Roberto Carlos',apellidos: 'Choque Poma'}),
       (ct4:Cuenta {nro_cuenta: 'UNI-000004', id_banco: 1, saldo: 29100.00,   saldo_cifrado: false, ci_cifrado: true}),
       (c4)-[:TIENE_CUENTA]->(ct4), (ct4)-[:PERTENECE_A]->(b)
CREATE (c5:Cliente {ci: '7500001', nombres: 'Elena Patricia',apellidos: 'Condori Quispe'}),
       (ct5:Cuenta {nro_cuenta: 'UNI-000005', id_banco: 1, saldo: 125000.00,  saldo_cifrado: true,  ci_cifrado: true}),
       (c5)-[:TIENE_CUENTA]->(ct5), (ct5)-[:PERTENECE_A]->(b);

// ── Banco 2 — Mercantil (Atbash / MySQL) — 5 cuentas ──────────────────────────
MATCH (b:Banco {id: 2}) WITH b
CREATE (c1:Cliente {ci: '7100002', nombres: 'Andrés Felipe',   apellidos: 'Heredia Loza'}),
       (ct1:Cuenta {nro_cuenta: 'MSC-000001', id_banco: 2, saldo: 18500.00,  saldo_cifrado: false, ci_cifrado: true}),
       (c1)-[:TIENE_CUENTA]->(ct1), (ct1)-[:PERTENECE_A]->(b)
CREATE (c2:Cliente {ci: '7200002', nombres: 'Sofía Valentina', apellidos: 'López Torres'}),
       (ct2:Cuenta {nro_cuenta: 'MSC-000002', id_banco: 2, saldo: 42000.00,  saldo_cifrado: false, ci_cifrado: true}),
       (c2)-[:TIENE_CUENTA]->(ct2), (ct2)-[:PERTENECE_A]->(b)
CREATE (c3:Cliente {ci: '7300002', nombres: 'Miguel Ángel',    apellidos: 'Vega Salinas'}),
       (ct3:Cuenta {nro_cuenta: 'MSC-000003', id_banco: 2, saldo: 7100.25,   saldo_cifrado: false, ci_cifrado: true}),
       (c3)-[:TIENE_CUENTA]->(ct3), (ct3)-[:PERTENECE_A]->(b)
CREATE (c4:Cliente {ci: '7400002', nombres: 'Laura Isabel',    apellidos: 'Ibáñez Cruz'}),
       (ct4:Cuenta {nro_cuenta: 'MSC-000004', id_banco: 2, saldo: 3300.80,   saldo_cifrado: false, ci_cifrado: true}),
       (c4)-[:TIENE_CUENTA]->(ct4), (ct4)-[:PERTENECE_A]->(b)
CREATE (c5:Cliente {ci: '7500002', nombres: 'Carlos Eduardo',  apellidos: 'Lima Medina'}),
       (ct5:Cuenta {nro_cuenta: 'MSC-000005', id_banco: 2, saldo: 210000.00, saldo_cifrado: true,  ci_cifrado: true}),
       (c5)-[:TIENE_CUENTA]->(ct5), (ct5)-[:PERTENECE_A]->(b);

// ── Banco 3 — BNB (Vigenère / MySQL) — 5 cuentas ─────────────────────────────
MATCH (b:Banco {id: 3}) WITH b
CREATE (c1:Cliente {ci: '7100003', nombres: 'Patricia Ximena', apellidos: 'Zarate Morales'}),
       (ct1:Cuenta {nro_cuenta: 'BNB-000001', id_banco: 3, saldo: 9600.00,    saldo_cifrado: false, ci_cifrado: true}),
       (c1)-[:TIENE_CUENTA]->(ct1), (ct1)-[:PERTENECE_A]->(b)
CREATE (c2:Cliente {ci: '7200003', nombres: 'Fernando José',   apellidos: 'Nava Salinas'}),
       (ct2:Cuenta {nro_cuenta: 'BNB-000002', id_banco: 3, saldo: 23000.75,   saldo_cifrado: false, ci_cifrado: true}),
       (c2)-[:TIENE_CUENTA]->(ct2), (ct2)-[:PERTENECE_A]->(b)
CREATE (c3:Cliente {ci: '7300003', nombres: 'Gabriela Paola',  apellidos: 'Oporto Vargas'}),
       (ct3:Cuenta {nro_cuenta: 'BNB-000003', id_banco: 3, saldo: 5500.00,    saldo_cifrado: false, ci_cifrado: true}),
       (c3)-[:TIENE_CUENTA]->(ct3), (ct3)-[:PERTENECE_A]->(b)
CREATE (c4:Cliente {ci: '7400003', nombres: 'Ernesto Manuel',  apellidos: 'Quispe Rojas'}),
       (ct4:Cuenta {nro_cuenta: 'BNB-000004', id_banco: 3, saldo: 71200.50,   saldo_cifrado: false, ci_cifrado: true}),
       (c4)-[:TIENE_CUENTA]->(ct4), (ct4)-[:PERTENECE_A]->(b)
CREATE (c5:Cliente {ci: '7500003', nombres: 'Mónica Sandra',   apellidos: 'Reyes Condori'}),
       (ct5:Cuenta {nro_cuenta: 'BNB-000005', id_banco: 3, saldo: 500000.00,  saldo_cifrado: true,  ci_cifrado: true}),
       (c5)-[:TIENE_CUENTA]->(ct5), (ct5)-[:PERTENECE_A]->(b);

// ── Banco 4 — BCP (Playfair / MySQL) — 5 cuentas ─────────────────────────────
MATCH (b:Banco {id: 4}) WITH b
CREATE (c1:Cliente {ci: '7100004', nombres: 'Diana Alejandra',  apellidos: 'Lima Huanca'}),
       (ct1:Cuenta {nro_cuenta: 'BCP-000001', id_banco: 4, saldo: 32000.00,   saldo_cifrado: false, ci_cifrado: true}),
       (c1)-[:TIENE_CUENTA]->(ct1), (ct1)-[:PERTENECE_A]->(b)
CREATE (c2:Cliente {ci: '7200004', nombres: 'Gustavo Alonso',   apellidos: 'Mamani Aguirre'}),
       (ct2:Cuenta {nro_cuenta: 'BCP-000002', id_banco: 4, saldo: 4800.50,    saldo_cifrado: false, ci_cifrado: true}),
       (c2)-[:TIENE_CUENTA]->(ct2), (ct2)-[:PERTENECE_A]->(b)
CREATE (c3:Cliente {ci: '7300004', nombres: 'Claudia Beatriz',  apellidos: 'Nogales Barriga'}),
       (ct3:Cuenta {nro_cuenta: 'BCP-000003', id_banco: 4, saldo: 88000.00,   saldo_cifrado: false, ci_cifrado: true}),
       (c3)-[:TIENE_CUENTA]->(ct3), (ct3)-[:PERTENECE_A]->(b)
CREATE (c4:Cliente {ci: '7400004', nombres: 'Hector Orlando',   apellidos: 'Orellana López'}),
       (ct4:Cuenta {nro_cuenta: 'BCP-000004', id_banco: 4, saldo: 12500.75,   saldo_cifrado: false, ci_cifrado: true}),
       (c4)-[:TIENE_CUENTA]->(ct4), (ct4)-[:PERTENECE_A]->(b)
CREATE (c5:Cliente {ci: '7500004', nombres: 'Vanessa Carolina', apellidos: 'Pinto Alcázar'}),
       (ct5:Cuenta {nro_cuenta: 'BCP-000005', id_banco: 4, saldo: 150000.00,  saldo_cifrado: true,  ci_cifrado: true}),
       (c5)-[:TIENE_CUENTA]->(ct5), (ct5)-[:PERTENECE_A]->(b);

// ── Banco 5 — BISA (Hill / MariaDB) — 5 cuentas ──────────────────────────────
MATCH (b:Banco {id: 5}) WITH b
CREATE (c1:Cliente {ci: '7100005', nombres: 'Diego Armando',  apellidos: 'Alcón Roca'}),
       (ct1:Cuenta {nro_cuenta: 'BISA-000001', id_banco: 5, saldo: 17200.00,   saldo_cifrado: false, ci_cifrado: true}),
       (c1)-[:TIENE_CUENTA]->(ct1), (ct1)-[:PERTENECE_A]->(b)
CREATE (c2:Cliente {ci: '7200005', nombres: 'Ximena Paola',   apellidos: 'Barrios Colque'}),
       (ct2:Cuenta {nro_cuenta: 'BISA-000002', id_banco: 5, saldo: 6500.75,    saldo_cifrado: false, ci_cifrado: true}),
       (c2)-[:TIENE_CUENTA]->(ct2), (ct2)-[:PERTENECE_A]->(b)
CREATE (c3:Cliente {ci: '7300005', nombres: 'Yolanda Cecilia', apellidos: 'Camacho Inca'}),
       (ct3:Cuenta {nro_cuenta: 'BISA-000003', id_banco: 5, saldo: 39800.50,   saldo_cifrado: false, ci_cifrado: true}),
       (c3)-[:TIENE_CUENTA]->(ct3), (ct3)-[:PERTENECE_A]->(b)
CREATE (c4:Cliente {ci: '7400005', nombres: 'Alfredo Rodrigo', apellidos: 'Durán Jiménez'}),
       (ct4:Cuenta {nro_cuenta: 'BISA-000004', id_banco: 5, saldo: 2100.00,    saldo_cifrado: false, ci_cifrado: true}),
       (c4)-[:TIENE_CUENTA]->(ct4), (ct4)-[:PERTENECE_A]->(b)
CREATE (c5:Cliente {ci: '7500005', nombres: 'Beatriz Lorena',  apellidos: 'Espinoza Flores'}),
       (ct5:Cuenta {nro_cuenta: 'BISA-000005', id_banco: 5, saldo: 320000.00,  saldo_cifrado: true,  ci_cifrado: true}),
       (c5)-[:TIENE_CUENTA]->(ct5), (ct5)-[:PERTENECE_A]->(b);

// ── Banco 6 — Ganadero (DES / MariaDB) — 5 cuentas ───────────────────────────
MATCH (b:Banco {id: 6}) WITH b
CREATE (c1:Cliente {ci: '7100006', nombres: 'Elena Sofía',    apellidos: 'Soria Cruz'}),
       (ct1:Cuenta {nro_cuenta: 'GAN-000001', id_banco: 6, saldo: 54000.00,   saldo_cifrado: false, ci_cifrado: true}),
       (c1)-[:TIENE_CUENTA]->(ct1), (ct1)-[:PERTENECE_A]->(b)
CREATE (c2:Cliente {ci: '7200006', nombres: 'Felipe Andrés',  apellidos: 'Torrez Mamani'}),
       (ct2:Cuenta {nro_cuenta: 'GAN-000002', id_banco: 6, saldo: 8900.50,    saldo_cifrado: false, ci_cifrado: true}),
       (c2)-[:TIENE_CUENTA]->(ct2), (ct2)-[:PERTENECE_A]->(b)
CREATE (c3:Cliente {ci: '7300006', nombres: 'Gonzalo Rodrigo', apellidos: 'Ureña Salinas'}),
       (ct3:Cuenta {nro_cuenta: 'GAN-000003', id_banco: 6, saldo: 23600.75,   saldo_cifrado: false, ci_cifrado: true}),
       (c3)-[:TIENE_CUENTA]->(ct3), (ct3)-[:PERTENECE_A]->(b)
CREATE (c4:Cliente {ci: '7400006', nombres: 'Hilda Rosa',      apellidos: 'Vaca Morales'}),
       (ct4:Cuenta {nro_cuenta: 'GAN-000004', id_banco: 6, saldo: 1500.00,    saldo_cifrado: false, ci_cifrado: true}),
       (c4)-[:TIENE_CUENTA]->(ct4), (ct4)-[:PERTENECE_A]->(b)
CREATE (c5:Cliente {ci: '7500006', nombres: 'Ignacio Rafael',  apellidos: 'Poma Vargas'}),
       (ct5:Cuenta {nro_cuenta: 'GAN-000005', id_banco: 6, saldo: 107000.00,  saldo_cifrado: true,  ci_cifrado: true}),
       (c5)-[:TIENE_CUENTA]->(ct5), (ct5)-[:PERTENECE_A]->(b);

// ── Banco 7 — Económico (3DES / MariaDB) — 5 cuentas ─────────────────────────
MATCH (b:Banco {id: 7}) WITH b
CREATE (c1:Cliente {ci: '7100007', nombres: 'Marco Antonio',    apellidos: 'López Ibáñez'}),
       (ct1:Cuenta {nro_cuenta: 'ECO-000001', id_banco: 7, saldo: 11400.00,   saldo_cifrado: false, ci_cifrado: true}),
       (c1)-[:TIENE_CUENTA]->(ct1), (ct1)-[:PERTENECE_A]->(b)
CREATE (c2:Cliente {ci: '7200007', nombres: 'Natalia Fernanda', apellidos: 'Mercado García'}),
       (ct2:Cuenta {nro_cuenta: 'ECO-000002', id_banco: 7, saldo: 63000.75,   saldo_cifrado: false, ci_cifrado: true}),
       (c2)-[:TIENE_CUENTA]->(ct2), (ct2)-[:PERTENECE_A]->(b)
CREATE (c3:Cliente {ci: '7300007', nombres: 'Omar Sebastián',   apellidos: 'Nava Roca'}),
       (ct3:Cuenta {nro_cuenta: 'ECO-000003', id_banco: 7, saldo: 4200.50,    saldo_cifrado: false, ci_cifrado: true}),
       (c3)-[:TIENE_CUENTA]->(ct3), (ct3)-[:PERTENECE_A]->(b)
CREATE (c4:Cliente {ci: '7400007', nombres: 'Pamela Cristina',  apellidos: 'Orellana Cruz'}),
       (ct4:Cuenta {nro_cuenta: 'ECO-000004', id_banco: 7, saldo: 28500.00,   saldo_cifrado: false, ci_cifrado: true}),
       (c4)-[:TIENE_CUENTA]->(ct4), (ct4)-[:PERTENECE_A]->(b)
CREATE (c5:Cliente {ci: '7500007', nombres: 'Quirino Alberto',  apellidos: 'Palacios Inca'}),
       (ct5:Cuenta {nro_cuenta: 'ECO-000005', id_banco: 7, saldo: 951000.00,  saldo_cifrado: true,  ci_cifrado: true}),
       (c5)-[:TIENE_CUENTA]->(ct5), (ct5)-[:PERTENECE_A]->(b);

// ── Banco 8 — Prodem (Blowfish / MariaDB) — 5 cuentas ────────────────────────
MATCH (b:Banco {id: 8}) WITH b
CREATE (c1:Cliente {ci: '7100008', nombres: 'Laura Viviana',   apellidos: 'Choque Vargas'}),
       (ct1:Cuenta {nro_cuenta: 'PROD-000001', id_banco: 8, saldo: 6800.00,   saldo_cifrado: false, ci_cifrado: true}),
       (c1)-[:TIENE_CUENTA]->(ct1), (ct1)-[:PERTENECE_A]->(b)
CREATE (c2:Cliente {ci: '7200008', nombres: 'Sebastián Ariel', apellidos: 'Rivera Mamani'}),
       (ct2:Cuenta {nro_cuenta: 'PROD-000002', id_banco: 8, saldo: 14300.50,  saldo_cifrado: false, ci_cifrado: true}),
       (c2)-[:TIENE_CUENTA]->(ct2), (ct2)-[:PERTENECE_A]->(b)
CREATE (c3:Cliente {ci: '7300008', nombres: 'Teresa Graciela', apellidos: 'Salinas Quispe'}),
       (ct3:Cuenta {nro_cuenta: 'PROD-000003', id_banco: 8, saldo: 2900.75,   saldo_cifrado: false, ci_cifrado: true}),
       (c3)-[:TIENE_CUENTA]->(ct3), (ct3)-[:PERTENECE_A]->(b)
CREATE (c4:Cliente {ci: '7400008', nombres: 'Ulises Marcelo',  apellidos: 'Torrez Roca'}),
       (ct4:Cuenta {nro_cuenta: 'PROD-000004', id_banco: 8, saldo: 47000.00,  saldo_cifrado: false, ci_cifrado: true}),
       (c4)-[:TIENE_CUENTA]->(ct4), (ct4)-[:PERTENECE_A]->(b)
CREATE (c5:Cliente {ci: '7500008', nombres: 'Valeria Eugenia', apellidos: 'Ureña Flores'}),
       (ct5:Cuenta {nro_cuenta: 'PROD-000005', id_banco: 8, saldo: 180000.00, saldo_cifrado: true,  ci_cifrado: true}),
       (c5)-[:TIENE_CUENTA]->(ct5), (ct5)-[:PERTENECE_A]->(b);

// ── Banco 9 — Solidario (Twofish / MongoDB) — 5 cuentas ──────────────────────
MATCH (b:Banco {id: 9}) WITH b
CREATE (c1:Cliente {ci: '7100009', nombres: 'Paola Marcela',  apellidos: 'Mamani Torres'}),
       (ct1:Cuenta {nro_cuenta: 'SOLD-000001', id_banco: 9, saldo: 3400.00,    saldo_cifrado: false, ci_cifrado: true}),
       (c1)-[:TIENE_CUENTA]->(ct1), (ct1)-[:PERTENECE_A]->(b)
CREATE (c2:Cliente {ci: '7200009', nombres: 'Beatriz Carmen', apellidos: 'Nogales Condori'}),
       (ct2:Cuenta {nro_cuenta: 'SOLD-000002', id_banco: 9, saldo: 9800.50,    saldo_cifrado: false, ci_cifrado: true}),
       (c2)-[:TIENE_CUENTA]->(ct2), (ct2)-[:PERTENECE_A]->(b)
CREATE (c3:Cliente {ci: '7300009', nombres: 'César Augusto',  apellidos: 'Ortuño Vargas'}),
       (ct3:Cuenta {nro_cuenta: 'SOLD-000003', id_banco: 9, saldo: 21500.75,   saldo_cifrado: false, ci_cifrado: true}),
       (c3)-[:TIENE_CUENTA]->(ct3), (ct3)-[:PERTENECE_A]->(b)
CREATE (c4:Cliente {ci: '7400009', nombres: 'Diana Elizabeth', apellidos: 'Ponce Alarcón'}),
       (ct4:Cuenta {nro_cuenta: 'SOLD-000004', id_banco: 9, saldo: 670.00,     saldo_cifrado: false, ci_cifrado: true}),
       (c4)-[:TIENE_CUENTA]->(ct4), (ct4)-[:PERTENECE_A]->(b)
CREATE (c5:Cliente {ci: '7500009', nombres: 'Emilio Enrique', apellidos: 'Quispe Tarqui'}),
       (ct5:Cuenta {nro_cuenta: 'SOLD-000005', id_banco: 9, saldo: 250000.00,  saldo_cifrado: true,  ci_cifrado: true}),
       (c5)-[:TIENE_CUENTA]->(ct5), (ct5)-[:PERTENECE_A]->(b);

// ── Banco 10 — Fortaleza (AES / MongoDB) — 5 cuentas ─────────────────────────
MATCH (b:Banco {id: 10}) WITH b
CREATE (c1:Cliente {ci: '7100010', nombres: 'Jhon Alejandro', apellidos: 'Camacho Pinto'}),
       (ct1:Cuenta {nro_cuenta: 'FORT-000001', id_banco: 10, saldo: 12900.00,  saldo_cifrado: false, ci_cifrado: true}),
       (c1)-[:TIENE_CUENTA]->(ct1), (ct1)-[:PERTENECE_A]->(b)
CREATE (c2:Cliente {ci: '7200010', nombres: 'Fanny Denisse',  apellidos: 'Rojas Medina'}),
       (ct2:Cuenta {nro_cuenta: 'FORT-000002', id_banco: 10, saldo: 5600.75,   saldo_cifrado: false, ci_cifrado: true}),
       (c2)-[:TIENE_CUENTA]->(ct2), (ct2)-[:PERTENECE_A]->(b)
CREATE (c3:Cliente {ci: '7300010', nombres: 'Gabriel Ricardo', apellidos: 'Saucedo Ibáñez'}),
       (ct3:Cuenta {nro_cuenta: 'FORT-000003', id_banco: 10, saldo: 88000.50,  saldo_cifrado: false, ci_cifrado: true}),
       (c3)-[:TIENE_CUENTA]->(ct3), (ct3)-[:PERTENECE_A]->(b)
CREATE (c4:Cliente {ci: '7400010', nombres: 'Hilda Susana',   apellidos: 'Torrez Gutiérrez'}),
       (ct4:Cuenta {nro_cuenta: 'FORT-000004', id_banco: 10, saldo: 3100.00,   saldo_cifrado: false, ci_cifrado: true}),
       (c4)-[:TIENE_CUENTA]->(ct4), (ct4)-[:PERTENECE_A]->(b)
CREATE (c5:Cliente {ci: '7500010', nombres: 'Ivan Rodrigo',   apellidos: 'Villca Inca'}),
       (ct5:Cuenta {nro_cuenta: 'FORT-000005', id_banco: 10, saldo: 145000.00, saldo_cifrado: true,  ci_cifrado: true}),
       (c5)-[:TIENE_CUENTA]->(ct5), (ct5)-[:PERTENECE_A]->(b);

// ── Banco 11 — FIE (RSA / PostgreSQL) — 5 cuentas ────────────────────────────
MATCH (b:Banco {id: 11}) WITH b
CREATE (c1:Cliente {ci: '7100011', nombres: 'Sofía del Carmen',  apellidos: 'Mamani Quispe'}),
       (ct1:Cuenta {nro_cuenta: 'FIE-100001', id_banco: 11, saldo: 15000.00,  saldo_cifrado: false, ci_cifrado: true}),
       (c1)-[:TIENE_CUENTA]->(ct1), (ct1)-[:PERTENECE_A]->(b)
CREATE (c2:Cliente {ci: '7200011', nombres: 'Carlos Roberto',    apellidos: 'Torrez Vargas'}),
       (ct2:Cuenta {nro_cuenta: 'FIE-100002', id_banco: 11, saldo: 8500.50,   saldo_cifrado: false, ci_cifrado: true}),
       (c2)-[:TIENE_CUENTA]->(ct2), (ct2)-[:PERTENECE_A]->(b)
CREATE (c3:Cliente {ci: '7300011', nombres: 'Ana Patricia',      apellidos: 'López Flores'}),
       (ct3:Cuenta {nro_cuenta: 'FIE-100003', id_banco: 11, saldo: 22300.75,  saldo_cifrado: false, ci_cifrado: true}),
       (c3)-[:TIENE_CUENTA]->(ct3), (ct3)-[:PERTENECE_A]->(b)
CREATE (c4:Cliente {ci: '7400011', nombres: 'Miguel Ernesto',    apellidos: 'Condori Apaza'}),
       (ct4:Cuenta {nro_cuenta: 'FIE-100004', id_banco: 11, saldo: 3200.00,   saldo_cifrado: false, ci_cifrado: true}),
       (c4)-[:TIENE_CUENTA]->(ct4), (ct4)-[:PERTENECE_A]->(b)
CREATE (c5:Cliente {ci: '7500011', nombres: 'Valentina Rosa',    apellidos: 'Rojas Mendoza'}),
       (ct5:Cuenta {nro_cuenta: 'FIE-100005', id_banco: 11, saldo: 470000.00, saldo_cifrado: true,  ci_cifrado: true}),
       (c5)-[:TIENE_CUENTA]->(ct5), (ct5)-[:PERTENECE_A]->(b);

// ── Banco 12 — PYME (ElGamal / PostgreSQL) — 5 cuentas ───────────────────────
MATCH (b:Banco {id: 12}) WITH b
CREATE (c1:Cliente {ci: '7100012', nombres: 'Roberto Guillermo', apellidos: 'Gutiérrez Luna'}),
       (ct1:Cuenta {nro_cuenta: 'PYME-200001', id_banco: 12, saldo: 9000.00,   saldo_cifrado: false, ci_cifrado: true}),
       (c1)-[:TIENE_CUENTA]->(ct1), (ct1)-[:PERTENECE_A]->(b)
CREATE (c2:Cliente {ci: '7200012', nombres: 'Patricia Soledad',  apellidos: 'Salinas Cruz'}),
       (ct2:Cuenta {nro_cuenta: 'PYME-200002', id_banco: 12, saldo: 14500.00,  saldo_cifrado: false, ci_cifrado: true}),
       (c2)-[:TIENE_CUENTA]->(ct2), (ct2)-[:PERTENECE_A]->(b)
CREATE (c3:Cliente {ci: '7300012', nombres: 'Juan Carlos',        apellidos: 'Huanca Mamani'}),
       (ct3:Cuenta {nro_cuenta: 'PYME-200003', id_banco: 12, saldo: 600.75,    saldo_cifrado: false, ci_cifrado: true}),
       (c3)-[:TIENE_CUENTA]->(ct3), (ct3)-[:PERTENECE_A]->(b)
CREATE (c4:Cliente {ci: '7400012', nombres: 'Isabel Marcela',    apellidos: 'Choque Inca'}),
       (ct4:Cuenta {nro_cuenta: 'PYME-200004', id_banco: 12, saldo: 31200.00,  saldo_cifrado: false, ci_cifrado: true}),
       (c4)-[:TIENE_CUENTA]->(ct4), (ct4)-[:PERTENECE_A]->(b)
CREATE (c5:Cliente {ci: '7500012', nombres: 'Fernando Raúl',     apellidos: 'Arce Roca'}),
       (ct5:Cuenta {nro_cuenta: 'PYME-200005', id_banco: 12, saldo: 580000.00, saldo_cifrado: true,  ci_cifrado: true}),
       (c5)-[:TIENE_CUENTA]->(ct5), (ct5)-[:PERTENECE_A]->(b);

// ── Banco 13 — Desarrollo Productivo (ECC / PostgreSQL) — 5 cuentas ──────────
MATCH (b:Banco {id: 13}) WITH b
CREATE (c1:Cliente {ci: '7100013', nombres: 'Daniela Paola',   apellidos: 'Poma Quisbert'}),
       (ct1:Cuenta {nro_cuenta: 'BDP-300001', id_banco: 13, saldo: 120000.00,  saldo_cifrado: true,  ci_cifrado: true}),
       (c1)-[:TIENE_CUENTA]->(ct1), (ct1)-[:PERTENECE_A]->(b)
CREATE (c2:Cliente {ci: '7200013', nombres: 'Andrés Fabio',    apellidos: 'Vega Soria'}),
       (ct2:Cuenta {nro_cuenta: 'BDP-300002', id_banco: 13, saldo: 85000.50,   saldo_cifrado: false, ci_cifrado: true}),
       (c2)-[:TIENE_CUENTA]->(ct2), (ct2)-[:PERTENECE_A]->(b)
CREATE (c3:Cliente {ci: '7300013', nombres: 'Claudia Patricia', apellidos: 'Mercado Ibáñez'}),
       (ct3:Cuenta {nro_cuenta: 'BDP-300003', id_banco: 13, saldo: 210000.00,  saldo_cifrado: true,  ci_cifrado: true}),
       (c3)-[:TIENE_CUENTA]->(ct3), (ct3)-[:PERTENECE_A]->(b)
CREATE (c4:Cliente {ci: '7400013', nombres: 'Ernesto David',   apellidos: 'Llano Colque'}),
       (ct4:Cuenta {nro_cuenta: 'BDP-300004', id_banco: 13, saldo: 43000.75,   saldo_cifrado: false, ci_cifrado: true}),
       (c4)-[:TIENE_CUENTA]->(ct4), (ct4)-[:PERTENECE_A]->(b)
CREATE (c5:Cliente {ci: '7500013', nombres: 'Mónica Elena',    apellidos: 'Ureña Balcázar'}),
       (ct5:Cuenta {nro_cuenta: 'BDP-300005', id_banco: 13, saldo: 760000.00,  saldo_cifrado: true,  ci_cifrado: true}),
       (c5)-[:TIENE_CUENTA]->(ct5), (ct5)-[:PERTENECE_A]->(b);

// ── Banco 14 — Nación Argentina (ChaCha20 / Redis) — 5 cuentas ───────────────
MATCH (b:Banco {id: 14}) WITH b
CREATE (c1:Cliente {ci: '7100014', nombres: 'Gabriela Fernanda', apellidos: 'Núñez Carrasco'}),
       (ct1:Cuenta {nro_cuenta: 'NACIARG-0001', id_banco: 14, saldo: 8500.00,    saldo_cifrado: false, ci_cifrado: true}),
       (c1)-[:TIENE_CUENTA]->(ct1), (ct1)-[:PERTENECE_A]->(b)
CREATE (c2:Cliente {ci: '7200014', nombres: 'Alejandro Manuel', apellidos: 'Castro Pereyra'}),
       (ct2:Cuenta {nro_cuenta: 'NACIARG-0002', id_banco: 14, saldo: 17000.50,   saldo_cifrado: false, ci_cifrado: true}),
       (c2)-[:TIENE_CUENTA]->(ct2), (ct2)-[:PERTENECE_A]->(b)
CREATE (c3:Cliente {ci: '7300014', nombres: 'Valentina Ines',   apellidos: 'Rodríguez Lima'}),
       (ct3:Cuenta {nro_cuenta: 'NACIARG-0003', id_banco: 14, saldo: 3200.75,    saldo_cifrado: false, ci_cifrado: true}),
       (c3)-[:TIENE_CUENTA]->(ct3), (ct3)-[:PERTENECE_A]->(b)
CREATE (c4:Cliente {ci: '7400014', nombres: 'Lucas Emanuel',    apellidos: 'González Torrez'}),
       (ct4:Cuenta {nro_cuenta: 'NACIARG-0004', id_banco: 14, saldo: 95000.00,   saldo_cifrado: false, ci_cifrado: true}),
       (c4)-[:TIENE_CUENTA]->(ct4), (ct4)-[:PERTENECE_A]->(b)
CREATE (c5:Cliente {ci: '7500014', nombres: 'Camila Florencia', apellidos: 'Martínez Vargas'}),
       (ct5:Cuenta {nro_cuenta: 'NACIARG-0005', id_banco: 14, saldo: 350000.00,  saldo_cifrado: true,  ci_cifrado: true}),
       (c5)-[:TIENE_CUENTA]->(ct5), (ct5)-[:PERTENECE_A]->(b);

// ── Verificar carga ────────────────────────────────────────────────────────────
MATCH (c:Cliente)-[:TIENE_CUENTA]->(ct:Cuenta)-[:PERTENECE_A]->(b:Banco)
RETURN b.id AS BancoId, b.nombre AS Banco, count(ct) AS Cuentas
ORDER BY BancoId;
