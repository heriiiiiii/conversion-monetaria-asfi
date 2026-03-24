#!/usr/bin/env bash
# =============================================================
# validate.sh — Bloque 1, Tarea 10
# Verifica que las 14 bases fueron cargadas correctamente.
# Genera reporte con conteo, campos cifrados y NULLs.
# Uso: bash scripts/validate.sh
# =============================================================
PASS=0; FAIL=0

ok()  { echo "  ✅ $1"; PASS=$((PASS+1)); }
err() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
chk() {
  # chk "label" COUNT_ACTUAL COUNT_EXPECTED
  if [ "$2" -eq "$3" ]; then
    ok "$1: $2 registros"
  else
    err "$1: esperados $3, encontrados $2"
  fi
}

echo "======================================================"
echo " 🔍 VALIDACIÓN — Sistema Bancario Distribuido"
echo "======================================================"

# ── PostgreSQL (FIE, PYME, Desarrollo) ───────────────────────────────────────
echo ""
echo "▶ PostgreSQL"
for DB in banco_fie banco_pyme banco_desarrollo_productivo; do
  TOTAL=$(docker exec banco_postgres psql -U admin -d "$DB" -At \
    -c "SELECT COUNT(*) FROM cuentas;" 2>/dev/null || echo "0")
  CI_CIFD=$(docker exec banco_postgres psql -U admin -d "$DB" -At \
    -c "SELECT COUNT(*) FROM cuentas WHERE ci_cifrado = TRUE;" 2>/dev/null || echo "0")
  SAL_NULL=$(docker exec banco_postgres psql -U admin -d "$DB" -At \
    -c "SELECT COUNT(*) FROM cuentas WHERE saldo_bs IS NULL;" 2>/dev/null || echo "0")
  echo "  📦 $DB → total=$TOTAL | ci_cifrado=$CI_CIFD | saldo_bs NULL=$SAL_NULL"
  [ "$TOTAL" -gt 0 ] && ok "$DB cargada" || err "$DB vacía"
  [ "$CI_CIFD" -eq "$TOTAL" ] && ok "$DB: todos los CI cifrados" || err "$DB: CI sin cifrar"
  [ "$SAL_NULL" -eq "$TOTAL" ] && ok "$DB: saldo_bs=NULL ✓" || err "$DB: saldo_bs tiene valores"
done

# ── MySQL (Unión, Mercantil, BNB, BCP) ───────────────────────────────────────
echo ""
echo "▶ MySQL"
for DB in banco_union banco_mercantil_santa_cruz banco_bnb banco_bcp; do
  TOTAL=$(docker exec banco_mysql mysql -uadmin -padmin123 -sN \
    -e "SELECT COUNT(*) FROM ${DB}.cuentas;" 2>/dev/null || echo "0")
  CI_CIFD=$(docker exec banco_mysql mysql -uadmin -padmin123 -sN \
    -e "SELECT COUNT(*) FROM ${DB}.cuentas WHERE ci_cifrado=1;" 2>/dev/null || echo "0")
  SAL_NULL=$(docker exec banco_mysql mysql -uadmin -padmin123 -sN \
    -e "SELECT COUNT(*) FROM ${DB}.cuentas WHERE saldo_bs IS NULL;" 2>/dev/null || echo "0")
  echo "  📦 $DB → total=$TOTAL | ci_cifrado=$CI_CIFD | saldo_bs NULL=$SAL_NULL"
  [ "$TOTAL" -gt 0 ] && ok "$DB cargada" || err "$DB vacía"
  [ "$CI_CIFD" -eq "$TOTAL" ] && ok "$DB: todos los CI cifrados" || err "$DB: CI sin cifrar"
done

# ── MariaDB (BISA, Ganadero, Económico, Prodem) ───────────────────────────────
echo ""
echo "▶ MariaDB"
for DB in banco_bisa banco_ganadero banco_economico banco_prodem; do
  TOTAL=$(docker exec banco_mariadb mysql -uadmin -padmin123 -sN \
    -e "SELECT COUNT(*) FROM ${DB}.cuentas;" 2>/dev/null || echo "0")
  CI_CIFD=$(docker exec banco_mariadb mysql -uadmin -padmin123 -sN \
    -e "SELECT COUNT(*) FROM ${DB}.cuentas WHERE ci_cifrado=1;" 2>/dev/null || echo "0")
  echo "  📦 $DB → total=$TOTAL | ci_cifrado=$CI_CIFD"
  [ "$TOTAL" -gt 0 ] && ok "$DB cargada" || err "$DB vacía"
  [ "$CI_CIFD" -eq "$TOTAL" ] && ok "$DB: todos los CI cifrados" || err "$DB: CI sin cifrar"
done

# ── MongoDB (Solidario, Fortaleza) ────────────────────────────────────────────
echo ""
echo "▶ MongoDB"
for DB in banco_solidario banco_fortaleza; do
  TOTAL=$(docker exec banco_mongodb mongosh -u admin -p admin123 \
    --authenticationDatabase admin --quiet \
    --eval "db=db.getSiblingDB('${DB}'); print(db.cuentas.countDocuments({}))" 2>/dev/null || echo "0")
  CI_CIFD=$(docker exec banco_mongodb mongosh -u admin -p admin123 \
    --authenticationDatabase admin --quiet \
    --eval "db=db.getSiblingDB('${DB}'); print(db.cuentas.countDocuments({ci_cifrado:true}))" 2>/dev/null || echo "0")
  echo "  📦 $DB → total=$TOTAL | ci_cifrado=$CI_CIFD"
  [ "$TOTAL" -gt 0 ] && ok "$DB cargada" || err "$DB vacía"
done

# ── Redis (Nación Argentina) ──────────────────────────────────────────────────
echo ""
echo "▶ Redis"
REDIS_KEYS=$(docker exec banco_redis redis-cli -a admin123 --no-auth-warning \
  --scan --pattern "cuenta:*" | wc -l | tr -d ' ')
echo "  📦 Redis → claves cuenta:*=$REDIS_KEYS"
[ "$REDIS_KEYS" -gt 0 ] && ok "Redis: Nación Argentina cargada" || err "Redis: sin datos"

# ── Neo4j ─────────────────────────────────────────────────────────────────────
echo ""
echo "▶ Neo4j"
NEO_CLIENTES=$(docker exec banco_neo4j cypher-shell -u neo4j -p admin123 \
  --format plain "MATCH (c:Cliente) RETURN count(c) AS n;" 2>/dev/null | tail -1 || echo "0")
NEO_CUENTAS=$(docker exec banco_neo4j cypher-shell -u neo4j -p admin123 \
  --format plain "MATCH (ct:Cuenta) RETURN count(ct) AS n;" 2>/dev/null | tail -1 || echo "0")
NEO_RELS=$(docker exec banco_neo4j cypher-shell -u neo4j -p admin123 \
  --format plain "MATCH ()-[:TIENE_CUENTA]->() RETURN count(*) AS n;" 2>/dev/null | tail -1 || echo "0")
echo "  📦 Neo4j → Clientes=$NEO_CLIENTES | Cuentas=$NEO_CUENTAS | Relaciones=$NEO_RELS"
[ "${NEO_CLIENTES:-0}" -gt 0 ] && ok "Neo4j: grafo cargado" || err "Neo4j: sin datos"

# ── Base Central ──────────────────────────────────────────────────────────────
echo ""
echo "▶ Base Central (PostgreSQL)"
BANCOS_CT=$(docker exec central_postgres psql -U central_admin -d central_db -At \
  -c "SELECT COUNT(*) FROM bancos;" 2>/dev/null || echo "0")
echo "  📦 central_db → bancos=$BANCOS_CT"
[ "$BANCOS_CT" -eq 14 ] && ok "central_db: 14 bancos registrados" || err "central_db: bancos=$BANCOS_CT (esperados 14)"

# ── Resumen final ─────────────────────────────────────────────────────────────
echo ""
echo "======================================================"
TOTAL_CHK=$((PASS+FAIL))
echo " RESULTADO: $PASS/$TOTAL_CHK verificaciones pasadas"
[ "$FAIL" -eq 0 ] && echo " ✅ Todo correcto" || echo " ⚠️  $FAIL verificaciones fallidas"
echo "======================================================"
