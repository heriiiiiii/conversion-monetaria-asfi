#!/usr/bin/env bash
# =============================================================
# populate.sh — Bloque 1, Tarea 5 & 8
# Procesa el CSV, aplica cifrado y puebla las 14 bases de datos.
# Uso: bash scripts/populate.sh
# =============================================================
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PROCESSED_DIR="$PROJECT_DIR/data/processed"

echo "======================================================"
echo " 🌱 POPULATE — Poblando las 14 bases de datos"
echo "======================================================"

# ── Paso 1: Procesar CSV y generar inserts cifrados ───────────────────────────
echo ""
echo "▶ Procesando CSV con cifrado selectivo..."
# "$PYTHON" "$SCRIPT_DIR/process_csv.py"
echo ""

# ── Paso 2: PostgreSQL (FIE, PYME, Desarrollo) ───────────────────────────────
echo "▶ PostgreSQL — cargando 3 bancos..."
for SQL_FILE in \
  "$PROCESSED_DIR/banco_11_banco_fie.sql" \
  "$PROCESSED_DIR/banco_12_banco_pyme.sql" \
  "$PROCESSED_DIR/banco_13_banco_desarrollo_productivo.sql"; do
  docker exec -i banco_postgres psql -U admin < "$SQL_FILE"
  echo "  ✅ $(basename $SQL_FILE)"
done

# ── Paso 3: MySQL (Unión, Mercantil, BNB, BCP) ───────────────────────────────
echo ""
echo "▶ MySQL — cargando 4 bancos..."
for SQL_FILE in \
  "$PROCESSED_DIR/banco_01_banco_union.sql" \
  "$PROCESSED_DIR/banco_02_banco_mercantil_santa_cruz.sql" \
  "$PROCESSED_DIR/banco_03_banco_bnb.sql" \
  "$PROCESSED_DIR/banco_04_banco_bcp.sql"; do
  docker exec -i banco_mysql mysql -uadmin -padmin123 < "$SQL_FILE"
  echo "  ✅ $(basename $SQL_FILE)"
done

# ── Paso 4: MariaDB (BISA, Ganadero, Económico, Prodem) ────────────────────-─
echo ""
echo "▶ MariaDB — cargando 4 bancos..."
for SQL_FILE in \
  "$PROCESSED_DIR/banco_05_banco_bisa.sql" \
  "$PROCESSED_DIR/banco_06_banco_ganadero.sql" \
  "$PROCESSED_DIR/banco_07_banco_economico.sql" \
  "$PROCESSED_DIR/banco_08_banco_prodem.sql"; do
  docker exec -i banco_mariadb mysql -uadmin -padmin123 < "$SQL_FILE"
  echo "  ✅ $(basename $SQL_FILE)"
done

# ── Paso 5: MongoDB (Solidario, Fortaleza) ────────────────────────────────────
echo ""
echo "▶ MongoDB — cargando 2 bancos..."
for JS_FILE in \
  "$PROCESSED_DIR/banco_09_banco_solidario.js" \
  "$PROCESSED_DIR/banco_10_banco_fortaleza.js"; do
  docker cp "$JS_FILE" banco_mongodb:/tmp/mongo_seed.js
  docker exec banco_mongodb mongosh -u admin -p admin123 \
    --authenticationDatabase admin --quiet /tmp/mongo_seed.js
  echo "  ✅ $(basename $JS_FILE)"
done

# ── Paso 6: Redis (Nación Argentina) ─────────────────────────────────────────
echo ""
echo "▶ Redis — cargando Banco Nación Argentina..."
REDIS_SH="$PROCESSED_DIR/banco_14_redis.sh"
docker cp "$REDIS_SH" banco_redis:/tmp/redis_seed.sh
docker exec banco_redis sh /tmp/redis_seed.sh
echo "  ✅ banco_14_redis.sh"

# ── Paso 7: Neo4j (grafo relacional) ─────────────────────────────────────────
echo ""
echo "▶ Neo4j — cargando grafo Cliente→Cuenta..."
docker exec banco_neo4j cypher-shell -u neo4j -p admin123 \
  --format plain \
  -f /var/lib/neo4j/import/init.cypher
echo "  ✅ init.cypher"

echo ""
echo "======================================================"
echo " ✅ Populate completado. Ejecuta 'bash scripts/validate.sh' para verificar."
echo "======================================================"
