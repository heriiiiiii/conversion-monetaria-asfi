// =============================================================
// MONGODB SEED — Datos adicionales de prueba
// =============================================================
// Bases de datos:
//   banco_solidario ← Banco Solidario (Twofish)
//   banco_fortaleza ← Banco Fortaleza (AES)
// Ejecutar con:
//   docker exec banco_mongodb mongosh \
//     -u admin -p admin123 \
//     --authenticationDatabase admin \
//     /scripts/seed_mongo.js
// =============================================================

// ── Solidario: actualizar saldo de una cuenta ──────────────
let solid = db.getSiblingDB('banco_solidario');
solid.cuentas.updateOne(
  { nro_cuenta: 'SOLD-000001' },
  { $set: { saldo: 5000.00, updated_at: new Date(), updated_user: 'seed_script' } }
);

// ── Solidario: cuenta adicional ────────────────────────────
solid.cuentas.insertOne({
  ci: '5467895',
  nombres: 'Francisca',
  apellidos: 'Ramos Soliz',
  nro_cuenta: 'SOLD-000006',
  id_banco: 9,
  saldo: 13400.00,
  code_verif: 'TWO-solid-006',
  created_at: new Date(),
  created_user: 'seed_script',
  updated_at: null,
  updated_user: null,
  deleted_at: null,
  deleted_user: null
});

// ── Fortaleza: cuenta adicional ────────────────────────────
let fort = db.getSiblingDB('banco_fortaleza');
fort.cuentas.insertOne({
  ci: '6578905',
  nombres: 'Gerardo',
  apellidos: 'Arancibia Molina',
  nro_cuenta: 'FORT-000006',
  id_banco: 10,
  saldo: 228500.00,
  code_verif: 'AES-fort-006',
  created_at: new Date(),
  created_user: 'seed_script',
  updated_at: null,
  updated_user: null,
  deleted_at: null,
  deleted_user: null
});

print('✅ Seed MongoDB adicional ejecutado correctamente.');
print('   Solidario total docs: ' + solid.cuentas.countDocuments());
print('   Fortaleza  total docs: ' + fort.cuentas.countDocuments());
