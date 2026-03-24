#!/usr/bin/env bash
# =============================================================
# reset.sh — Bloque 1, Tarea 5
# Trunca las tablas 'cuentas' de los 14 bancos.
# Agrega columnas nuevas si no existen (saldo_bs, ci_cifrado, saldo_cifrado).
# Uso: bash scripts/reset.sh
# =============================================================
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "======================================================"
echo " 🔄 RESET — Limpiando las 14 bases de datos"
echo "======================================================"

# ── PostgreSQL (FIE, PYME, Desarrollo) ────────────────────────────────────────
echo ""
echo "▶ PostgreSQL: banco_fie | banco_pyme | banco_desarrollo_productivo"
for DB in banco_fie banco_pyme banco_desarrollo_productivo; do
  docker exec banco_postgres psql -U admin -d "$DB" -q -c "
    ALTER TABLE cuentas ADD COLUMN IF NOT EXISTS saldo_bs      NUMERIC(18,2)  DEFAULT NULL;
    ALTER TABLE cuentas ADD COLUMN IF NOT EXISTS ci_cifrado    BOOLEAN        NOT NULL DEFAULT FALSE;
    ALTER TABLE cuentas ADD COLUMN IF NOT EXISTS saldo_cifrado BOOLEAN        NOT NULL DEFAULT FALSE;
    TRUNCATE TABLE cuentas RESTART IDENTITY;
  "
  echo "  ✅ $DB — truncada"
done

# ── MySQL (Unión, Mercantil, BNB, BCP) ───────────────────────────────────────
echo ""
echo "▶ MySQL: banco_union | banco_mercantil_santa_cruz | banco_bnb | banco_bcp"
for DB in banco_union banco_mercantil_santa_cruz banco_bnb banco_bcp; do
  # ADD COLUMN — ignorar si ya existe (MySQL no soporta IF NOT EXISTS)
  docker exec banco_mysql mysql -uadmin -padmin123 -e \
    "ALTER TABLE ${DB}.cuentas ADD COLUMN saldo_bs DECIMAL(18,2) DEFAULT NULL;" 2>/dev/null || true
  docker exec banco_mysql mysql -uadmin -padmin123 -e \
    "ALTER TABLE ${DB}.cuentas ADD COLUMN ci_cifrado TINYINT(1) NOT NULL DEFAULT 0;" 2>/dev/null || true
  docker exec banco_mysql mysql -uadmin -padmin123 -e \
    "ALTER TABLE ${DB}.cuentas ADD COLUMN saldo_cifrado TINYINT(1) NOT NULL DEFAULT 0;" 2>/dev/null || true
  docker exec banco_mysql mysql -uadmin -padmin123 -e \
    "TRUNCATE TABLE ${DB}.cuentas;"
  echo "  ✅ $DB — truncada"
done

# ── MariaDB (BISA, Ganadero, Económico, Prodem) ───────────────────────────────
echo ""
echo "▶ MariaDB: banco_bisa | banco_ganadero | banco_economico | banco_prodem"
for DB in banco_bisa banco_ganadero banco_economico banco_prodem; do
  docker exec banco_mariadb mysql -uadmin -padmin123 -e "
    ALTER TABLE ${DB}.cuentas ADD COLUMN IF NOT EXISTS saldo_bs DECIMAL(18,2) DEFAULT NULL;
    ALTER TABLE ${DB}.cuentas ADD COLUMN IF NOT EXISTS ci_cifrado TINYINT(1) NOT NULL DEFAULT 0;
    ALTER TABLE ${DB}.cuentas ADD COLUMN IF NOT EXISTS saldo_cifrado TINYINT(1) NOT NULL DEFAULT 0;
    TRUNCATE TABLE ${DB}.cuentas;
  "
  echo "  ✅ $DB — truncada"
done

# ── MongoDB (Solidario, Fortaleza) ────────────────────────────────────────────
echo ""
echo "▶ MongoDB: banco_solidario | banco_fortaleza"
for DB in banco_solidario banco_fortaleza; do
  docker exec banco_mongodb mongosh -u admin -p admin123 \
    --authenticationDatabase admin --quiet \
    --eval "db = db.getSiblingDB('${DB}'); db.cuentas.deleteMany({});" > /dev/null
  echo "  ✅ $DB — vaciada"
done

# ── Redis (Nación Argentina) ──────────────────────────────────────────────────
echo ""
echo "▶ Redis: eliminando claves cuenta:NACIARG-*"
docker exec banco_redis redis-cli -a admin123 --no-auth-warning \
  --scan --pattern "cuenta:NACIARG-*" | \
  xargs -r docker exec -i banco_redis redis-cli -a admin123 --no-auth-warning DEL > /dev/null
echo "  ✅ Redis — claves NACIARG eliminadas"

# ── Neo4j (Grafo) ─────────────────────────────────────────────────────────────
echo ""
echo "▶ Neo4j: eliminando todos los nodos y relaciones del grafo..."
docker exec banco_neo4j cypher-shell -u neo4j -p admin123 \
  --format plain \
  "MATCH (n) DETACH DELETE n;" > /dev/null 2>&1 || true
echo "  ✅ Neo4j — grafo limpio"

echo ""
echo "======================================================"
echo " ✅ Reset completado. Ejecuta 'bash scripts/populate.sh' para repoblar."
echo "======================================================"
