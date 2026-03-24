#!/bin/bash
# =============================================================
# REDIS SEED: Banco Nación Argentina — Cifrado ChaCha20
# =============================================================
# Inserta cuentas de prueba en Redis usando HSET (hashes).
# Cada cuenta es un hash con la clave: cuenta:<nro_cuenta>
# =============================================================

REDIS_CLI="redis-cli -a admin123"

echo "🏦 Cargando datos del Banco Nación Argentina (ChaCha20)..."

# ── Cuenta 1 ──────────────────────────────
$REDIS_CLI HSET "cuenta:NACIARG-0001" \
  ci         "2234567" \
  nombres    "Gabriela" \
  apellidos  "Núñez Carrasco" \
  nro_cuenta "NACIARG-0001" \
  id_banco   14 \
  saldo      "18500.00" \
  code_verif "CHACHA20-001" \
  created_at "2026-01-15T10:30:00" \
  created_user "admin"

# ── Cuenta 2 ──────────────────────────────
$REDIS_CLI HSET "cuenta:NACIARG-0002" \
  ci         "3345677" \
  nombres    "Hernan" \
  apellidos  "Basurto Rivera" \
  nro_cuenta "NACIARG-0002" \
  id_banco   14 \
  saldo      "7200.50" \
  code_verif "CHACHA20-002" \
  created_at "2026-01-20T14:15:00" \
  created_user "admin"

# ── Cuenta 3 ──────────────────────────────
$REDIS_CLI HSET "cuenta:NACIARG-0003" \
  ci         "4456787" \
  nombres    "Irene" \
  apellidos  "Carranza López" \
  nro_cuenta "NACIARG-0003" \
  id_banco   14 \
  saldo      "54300.75" \
  code_verif "CHACHA20-003" \
  created_at "2026-02-01T09:00:00" \
  created_user "admin"

# ── Cuenta 4 ──────────────────────────────
$REDIS_CLI HSET "cuenta:NACIARG-0004" \
  ci         "5567797" \
  nombres    "Javier" \
  apellidos  "Domínguez Ríos" \
  nro_cuenta "NACIARG-0004" \
  id_banco   14 \
  saldo      "2100.00" \
  code_verif "CHACHA20-004" \
  created_at "2026-02-10T11:45:00" \
  created_user "admin"

# ── Cuenta 5 ──────────────────────────────
$REDIS_CLI HSET "cuenta:NACIARG-0005" \
  ci         "6678807" \
  nombres    "Karina" \
  apellidos  "Espósito Vega" \
  nro_cuenta "NACIARG-0005" \
  id_banco   14 \
  saldo      "97600.00" \
  code_verif "CHACHA20-005" \
  created_at "2026-02-15T16:20:00" \
  created_user "admin"

# ── Índice por CI ──────────────────────────
$REDIS_CLI SADD "idx:ci:2234567" "cuenta:NACIARG-0001"
$REDIS_CLI SADD "idx:ci:3345677" "cuenta:NACIARG-0002"
$REDIS_CLI SADD "idx:ci:4456787" "cuenta:NACIARG-0003"
$REDIS_CLI SADD "idx:ci:5567797" "cuenta:NACIARG-0004"
$REDIS_CLI SADD "idx:ci:6678807" "cuenta:NACIARG-0005"

# ── Conjunto de todas las cuentas ─────────
$REDIS_CLI SADD "banco:14:cuentas" \
  "cuenta:NACIARG-0001" \
  "cuenta:NACIARG-0002" \
  "cuenta:NACIARG-0003" \
  "cuenta:NACIARG-0004" \
  "cuenta:NACIARG-0005"

echo "✅ 5 cuentas del Banco Nación Argentina cargadas en Redis."
echo "   Consultar con: redis-cli -a admin123 HGETALL 'cuenta:NACIARG-0001'"
