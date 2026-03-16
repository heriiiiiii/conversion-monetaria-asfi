// =============================================================
// MONGODB: Bancos Solidario (Twofish), Fortaleza (AES)
// =============================================================
// Nomenclatura de bases de datos:
//   banco_solidario  ← Banco Solidario (Twofish)
//   banco_fortaleza  ← Banco Fortaleza (AES)
// =============================================================

// ─────────────────────────────────────────
// BANCO SOLIDARIO — Cifrado Twofish
// Base de datos: banco_solidario
// ─────────────────────────────────────────
db = db.getSiblingDB('banco_solidario');

db.createCollection('cuentas', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['ci', 'nombres', 'apellidos', 'nro_cuenta', 'id_banco', 'saldo'],
      properties: {
        ci:           { bsonType: 'string', description: 'Cédula de identidad' },
        nombres:      { bsonType: 'string', description: 'Nombres del titular' },
        apellidos:    { bsonType: 'string', description: 'Apellidos del titular' },
        nro_cuenta:   { bsonType: 'string', description: 'Número de cuenta único' },
        id_banco:     { bsonType: 'int',    description: 'ID del banco (9 = Banco Solidario)' },
        saldo:        { bsonType: 'double', description: 'Saldo actual' },
        code_verif:   { bsonType: 'string', description: 'Número de cuenta cifrado con Twofish' },
        created_at:   { bsonType: 'date' },
        created_user: { bsonType: 'string' },
        updated_at:   { bsonType: ['date', 'null'] },
        updated_user: { bsonType: ['string', 'null'] },
        deleted_at:   { bsonType: ['date', 'null'] },
        deleted_user: { bsonType: ['string', 'null'] }
      }
    }
  }
});

db.cuentas.createIndex({ nro_cuenta: 1 }, { unique: true });
db.cuentas.createIndex({ ci: 1 });

db.cuentas.insertMany([
  {
    ci: '9012345',
    nombres: 'Paola',
    apellidos: 'Mamani Torres',
    nro_cuenta: 'SOLD-000001',
    id_banco: 9,
    saldo: 3400.00,
    code_verif: 'TWOFISH_ENC_001',
    created_at: new Date(),
    created_user: 'admin',
    updated_at: null,
    updated_user: null,
    deleted_at: null,
    deleted_user: null
  },
  {
    ci: '1023455',
    nombres: 'Beatriz',
    apellidos: 'Nogales Condori',
    nro_cuenta: 'SOLD-000002',
    id_banco: 9,
    saldo: 9800.50,
    code_verif: 'TWOFISH_ENC_002',
    created_at: new Date(),
    created_user: 'admin',
    updated_at: null,
    updated_user: null,
    deleted_at: null,
    deleted_user: null
  },
  {
    ci: '2134565',
    nombres: 'César',
    apellidos: 'Ortuño Vargas',
    nro_cuenta: 'SOLD-000003',
    id_banco: 9,
    saldo: 21500.75,
    code_verif: 'TWOFISH_ENC_003',
    created_at: new Date(),
    created_user: 'admin',
    updated_at: null,
    updated_user: null,
    deleted_at: null,
    deleted_user: null
  },
  {
    ci: '3245675',
    nombres: 'Diana',
    apellidos: 'Ponce Alarcón',
    nro_cuenta: 'SOLD-000004',
    id_banco: 9,
    saldo: 670.00,
    code_verif: 'TWOFISH_ENC_004',
    created_at: new Date(),
    created_user: 'admin',
    updated_at: null,
    updated_user: null,
    deleted_at: null,
    deleted_user: null
  },
  {
    ci: '4356785',
    nombres: 'Emilio',
    apellidos: 'Quispe Tarqui',
    nro_cuenta: 'SOLD-000005',
    id_banco: 9,
    saldo: 58000.00,
    code_verif: 'TWOFISH_ENC_005',
    created_at: new Date(),
    created_user: 'admin',
    updated_at: null,
    updated_user: null,
    deleted_at: null,
    deleted_user: null
  }
]);

print('✅ Banco Solidario (Twofish) — DB: banco_solidario — 5 documentos insertados.');

// ─────────────────────────────────────────
// BANCO FORTALEZA — Cifrado AES
// Base de datos: banco_fortaleza
// ─────────────────────────────────────────
db = db.getSiblingDB('banco_fortaleza');

db.createCollection('cuentas', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['ci', 'nombres', 'apellidos', 'nro_cuenta', 'id_banco', 'saldo'],
      properties: {
        ci:           { bsonType: 'string' },
        nombres:      { bsonType: 'string' },
        apellidos:    { bsonType: 'string' },
        nro_cuenta:   { bsonType: 'string' },
        id_banco:     { bsonType: 'int',    description: 'ID del banco (10 = Banco Fortaleza)' },
        saldo:        { bsonType: 'double' },
        code_verif:   { bsonType: 'string', description: 'Número de cuenta cifrado con AES' },
        created_at:   { bsonType: 'date' },
        created_user: { bsonType: 'string' },
        updated_at:   { bsonType: ['date', 'null'] },
        updated_user: { bsonType: ['string', 'null'] },
        deleted_at:   { bsonType: ['date', 'null'] },
        deleted_user: { bsonType: ['string', 'null'] }
      }
    }
  }
});

db.cuentas.createIndex({ nro_cuenta: 1 }, { unique: true });
db.cuentas.createIndex({ ci: 1 });

db.cuentas.insertMany([
  {
    ci: '1123456',
    nombres: 'Jhon',
    apellidos: 'Camacho Pinto',
    nro_cuenta: 'FORT-000001',
    id_banco: 10,
    saldo: 12900.00,
    code_verif: 'AES_ENC_001',
    created_at: new Date(),
    created_user: 'admin',
    updated_at: null,
    updated_user: null,
    deleted_at: null,
    deleted_user: null
  },
  {
    ci: '2234566',
    nombres: 'Fanny',
    apellidos: 'Rojas Medina',
    nro_cuenta: 'FORT-000002',
    id_banco: 10,
    saldo: 5600.75,
    code_verif: 'AES_ENC_002',
    created_at: new Date(),
    created_user: 'admin',
    updated_at: null,
    updated_user: null,
    deleted_at: null,
    deleted_user: null
  },
  {
    ci: '3345676',
    nombres: 'Gabriel',
    apellidos: 'Saucedo Ibáñez',
    nro_cuenta: 'FORT-000003',
    id_banco: 10,
    saldo: 88000.50,
    code_verif: 'AES_ENC_003',
    created_at: new Date(),
    created_user: 'admin',
    updated_at: null,
    updated_user: null,
    deleted_at: null,
    deleted_user: null
  },
  {
    ci: '4456786',
    nombres: 'Hilda',
    apellidos: 'Torrez Gutiérrez',
    nro_cuenta: 'FORT-000004',
    id_banco: 10,
    saldo: 3100.00,
    code_verif: 'AES_ENC_004',
    created_at: new Date(),
    created_user: 'admin',
    updated_at: null,
    updated_user: null,
    deleted_at: null,
    deleted_user: null
  },
  {
    ci: '5567796',
    nombres: 'Ivan',
    apellidos: 'Villca Inca',
    nro_cuenta: 'FORT-000005',
    id_banco: 10,
    saldo: 145000.00,
    code_verif: 'AES_ENC_005',
    created_at: new Date(),
    created_user: 'admin',
    updated_at: null,
    updated_user: null,
    deleted_at: null,
    deleted_user: null
  }
]);

print('✅ Banco Fortaleza (AES) — DB: banco_fortaleza — 5 documentos insertados.');
