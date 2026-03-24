// =============================================================
// MONGODB: Bancos Solidario (Twofish), Fortaleza (AES)
// =============================================================
// SOLO DDL — Los datos se cargan mediante scripts/populate.sh
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
        ci:           { bsonType: 'string',  description: 'CI cifrado con Twofish (base64)' },
        nombres:      { bsonType: 'string',  description: 'Nombres del titular' },
        apellidos:    { bsonType: 'string',  description: 'Apellidos del titular' },
        nro_cuenta:   { bsonType: 'string',  description: 'Número de cuenta único' },
        id_banco:     { bsonType: 'int',     description: 'ID del banco (9 = Banco Solidario)' },
        saldo:        { bsonType: 'string',  description: 'Saldo USD — puede ser base64(Twofish::valor) si saldo_cifrado=true' },
        saldo_bs:     { bsonType: ['double', 'null'], description: 'Saldo en bolivianos — inicia en null' },
        ci_cifrado:   { bsonType: 'bool',    description: 'Si el CI está cifrado' },
        saldo_cifrado:{ bsonType: 'bool',    description: 'Si el saldo en USD está cifrado' },
        code_verif:   { bsonType: ['string', 'null'], description: 'Código de verificación — inicia en null' },
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

print('✅ banco_solidario — colección cuentas creada (sin datos). Populate con scripts/populate.sh');

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
        ci:           { bsonType: 'string',  description: 'CI cifrado con AES (base64)' },
        nombres:      { bsonType: 'string' },
        apellidos:    { bsonType: 'string' },
        nro_cuenta:   { bsonType: 'string' },
        id_banco:     { bsonType: 'int',     description: 'ID del banco (10 = Banco Fortaleza)' },
        saldo:        { bsonType: 'string',  description: 'Saldo USD — puede ser base64(AES::valor) si saldo_cifrado=true' },
        saldo_bs:     { bsonType: ['double', 'null'] },
        ci_cifrado:   { bsonType: 'bool' },
        saldo_cifrado:{ bsonType: 'bool' },
        code_verif:   { bsonType: ['string', 'null'], description: 'Código de verificación — inicia en null' },
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

print('✅ banco_fortaleza — colección cuentas creada (sin datos). Populate con scripts/populate.sh');
