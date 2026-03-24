#!/usr/bin/env python3
"""
process_csv.py — Bloque 1, Tareas 6 & 7
Lee el dataset CSV, aplica cifrado selectivo y genera scripts de inserción por banco.

Política de cifrado:
  Identificacion → siempre cifrado  (base64(algoritmo::ci))
  Saldo          → cifrado si >= 100.000 USD
  SaldoBs        → siempre NULL en carga inicial
  CodigoVerif    → siempre NULL en carga inicial

Formato del CSV nuevo:
  Nro, Identificacion, Nombres, Apellidos, NroCuenta, IdBanco, Saldo

Uso: python scripts/process_csv.py [--csv ruta/al/csv]
"""

import csv
import os
import base64
import json
import argparse
from datetime import datetime

# ── Umbral de cifrado de saldo ────────────────────────────────────────────────
UMBRAL_USD = 100_000.00

# ── Configuración de los 14 bancos ───────────────────────────────────────────
BANK_CONFIG = {
    1: {"nombre": "Banco Unión", "algoritmo": "César", "motor": "mysql", "db": "banco_union"},
    2: {"nombre": "Banco Mercantil Santa Cruz", "algoritmo": "Atbash", "motor": "mysql", "db": "banco_mercantil_santa_cruz"},
    3: {"nombre": "Banco Nacional de Bolivia (BNB)", "algoritmo": "Vigenère", "motor": "mysql", "db": "banco_bnb"},
    4: {"nombre": "Banco de Crédito de Bolivia (BCP)", "algoritmo": "Playfair", "motor": "mysql", "db": "banco_bcp"},
    5: {"nombre": "Banco BISA", "algoritmo": "Hill", "motor": "mariadb", "db": "banco_bisa"},
    6: {"nombre": "Banco Ganadero", "algoritmo": "DES", "motor": "mariadb", "db": "banco_ganadero"},
    7: {"nombre": "Banco Económico", "algoritmo": "3DES", "motor": "mariadb", "db": "banco_economico"},
    8: {"nombre": "Banco Prodem", "algoritmo": "Blowfish", "motor": "mariadb", "db": "banco_prodem"},
    9: {"nombre": "Banco Solidario", "algoritmo": "Twofish", "motor": "mongodb", "db": "banco_solidario"},
    10: {"nombre": "Banco Fortaleza", "algoritmo": "AES", "motor": "mongodb", "db": "banco_fortaleza"},
    11: {"nombre": "Banco FIE", "algoritmo": "RSA", "motor": "postgres", "db": "banco_fie"},
    12: {"nombre": "Banco PYME", "algoritmo": "ElGamal", "motor": "postgres", "db": "banco_pyme"},
    13: {"nombre": "Banco de Desarrollo Productivo", "algoritmo": "ECC", "motor": "postgres", "db": "banco_desarrollo_productivo"},
    14: {"nombre": "Banco Nación Argentina", "algoritmo": "ChaCha20", "motor": "redis", "db": "0"},
}

# Mapeo de columnas del CSV (soporta ambos formatos: antiguo y nuevo)
COL_MAP_NEW = {
    "cuenta_id": "Nro",
    "ci": "Identificacion",
    "nombres": "Nombres",
    "apellidos": "Apellidos",
    "nro_cuenta": "NroCuenta",
    "banco_id": "IdBanco",
    "saldo": "Saldo",
}
COL_MAP_OLD = {
    "cuenta_id": "CuentaId",
    "ci": "CI",
    "nombres": "Nombres",
    "apellidos": "Apellidos",
    "nro_cuenta": "NroCuenta",
    "banco_id": "BancoId",
    "saldo": "SaldoUSD",
}


def cifrar(algoritmo: str, valor: str) -> str:
    """Cifrado simulado académico: base64(ALGORITMO::valor)"""
    raw = f"{algoritmo}::{valor}".encode("utf-8")
    return base64.b64encode(raw).decode("utf-8")


def detect_columns(header: list[str]) -> dict:
    """Detecta automáticamente si el CSV usa el formato nuevo o viejo."""
    header_set = set(header or [])
    if "IdBanco" in header_set:
        print("📋 Formato detectado: NUEVO (Nro, Identificacion, IdBanco, Saldo)")
        return COL_MAP_NEW
    print("📋 Formato detectado: ANTIGUO (CuentaId, CI, BancoId, SaldoUSD)")
    return COL_MAP_OLD


def procesar(csv_path: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    bancos_data = {bid: [] for bid in BANK_CONFIG}
    stats = {bid: {"total": 0, "ci_cifrados": 0, "saldo_cifrados": 0} for bid in BANK_CONFIG}
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_rows = 0
    skipped = 0
    col_map: dict = {}

    # Control de inconsistencias
    seen_accounts: set[tuple[int, str]] = set()
    inconsistencias: list[dict[str, str]] = []
    duplicates_skipped = 0

    print(f"📂 Leyendo: {csv_path}")
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        col_map = detect_columns(reader.fieldnames or [])

        for row_number, row in enumerate(reader, start=2):
            total_rows += 1
            try:
                bid = int(str(row[col_map["banco_id"]]).strip())
            except (ValueError, KeyError, TypeError):
                skipped += 1
                inconsistencias.append({
                    "fila": str(row_number),
                    "motivo": "BANCO_ID_INVALIDO",
                    "IdBanco": str(row.get(col_map.get("banco_id", ""), "")).strip(),
                    "NroCuenta": str(row.get(col_map.get("nro_cuenta", ""), "")).strip(),
                    "Identificacion": str(row.get(col_map.get("ci", ""), "")).strip(),
                    "Saldo": str(row.get(col_map.get("saldo", ""), "")).strip(),
                })
                continue

            if bid not in BANK_CONFIG:
                skipped += 1
                inconsistencias.append({
                    "fila": str(row_number),
                    "motivo": "BANCO_NO_CONFIGURADO",
                    "IdBanco": str(bid),
                    "NroCuenta": str(row.get(col_map.get("nro_cuenta", ""), "")).strip(),
                    "Identificacion": str(row.get(col_map.get("ci", ""), "")).strip(),
                    "Saldo": str(row.get(col_map.get("saldo", ""), "")).strip(),
                })
                continue

            cfg = BANK_CONFIG[bid]
            alg = cfg["algoritmo"]

            ci_raw = str(row.get(col_map["ci"], "")).strip()
            nombres = str(row.get(col_map["nombres"], "")).strip()
            apellidos = str(row.get(col_map["apellidos"], "")).strip()
            nro_cuenta = str(row.get(col_map["nro_cuenta"], "")).strip()
            saldo_raw = str(row.get(col_map["saldo"], "")).strip()

            # Validaciones mínimas y tolerantes
            if not nro_cuenta:
                skipped += 1
                inconsistencias.append({
                    "fila": str(row_number),
                    "motivo": "NRO_CUENTA_VACIO",
                    "IdBanco": str(bid),
                    "NroCuenta": nro_cuenta,
                    "Identificacion": ci_raw,
                    "Saldo": saldo_raw,
                })
                continue

            # Evitar que duplicados por (banco, nro_cuenta) detengan la carga
            unique_key = (bid, nro_cuenta)
            if unique_key in seen_accounts:
                skipped += 1
                duplicates_skipped += 1
                inconsistencias.append({
                    "fila": str(row_number),
                    "motivo": "CUENTA_DUPLICADA_EN_MISMO_BANCO",
                    "IdBanco": str(bid),
                    "NroCuenta": nro_cuenta,
                    "Identificacion": ci_raw,
                    "Saldo": saldo_raw,
                })
                continue
            seen_accounts.add(unique_key)

            try:
                saldo = float(saldo_raw)
            except (ValueError, TypeError):
                skipped += 1
                inconsistencias.append({
                    "fila": str(row_number),
                    "motivo": "SALDO_INVALIDO",
                    "IdBanco": str(bid),
                    "NroCuenta": nro_cuenta,
                    "Identificacion": ci_raw,
                    "Saldo": saldo_raw,
                })
                continue

            # ── Cifrado CI (siempre) ──────────────────────
            ci_enc = cifrar(alg, ci_raw)
            stats[bid]["ci_cifrados"] += 1

            # ── Cifrado Saldo (condicional) ───────────────
            if saldo >= UMBRAL_USD:
                saldo_enc = cifrar(alg, f"{saldo:.3f}")
                saldo_cifrado = True
                stats[bid]["saldo_cifrados"] += 1
            else:
                saldo_enc = f"{saldo:.3f}"
                saldo_cifrado = False

            bancos_data[bid].append(
                {
                    "nro_cuenta": nro_cuenta,
                    "ci": ci_enc,
                    "ci_cifrado": True,
                    "nombres": nombres,
                    "apellidos": apellidos,
                    "saldo": saldo_enc,
                    "saldo_cifrado": saldo_cifrado,
                    "banco_id": bid,
                }
            )
            stats[bid]["total"] += 1

    print(f"\n📊 Total leídas: {total_rows} | Omitidas: {skipped}")
    print(f"⚠️ Duplicados omitidos: {duplicates_skipped}")

    # ── Generar archivos por motor ────────────────────────────────────────────
    print("\n🔄 Generando scripts de inserción por banco...\n")
    for bid, registros in bancos_data.items():
        cfg = BANK_CONFIG[bid]
        motor = cfg["motor"]
        if not registros:
            print(f"  ⚠️  Banco {bid} ({cfg['nombre']}): sin registros válidos en el CSV")
            continue
        if motor == "postgres":
            _gen_postgres(bid, cfg, registros, now_str, output_dir)
        elif motor in ("mysql", "mariadb"):
            _gen_mysql(bid, cfg, registros, now_str, output_dir)
        elif motor == "mongodb":
            _gen_mongo(bid, cfg, registros, now_str, output_dir)
        elif motor == "redis":
            _gen_redis(bid, cfg, registros, now_str, output_dir)

    # ── Reporte ───────────────────────────────────────────────────────────────
    print("\n┌──────┬────────────────────────────────────────┬───────────┬───────────┬────────────┐")
    print("│  ID  │ Banco                                  │   Total   │ CI Cifr.  │ Saldo Cif. │")
    print("├──────┼────────────────────────────────────────┼───────────┼───────────┼────────────┤")
    for bid in sorted(stats):
        s = stats[bid]
        nombre = str(BANK_CONFIG[bid]["nombre"])[:40]
        print(f"│ {bid:4d} │ {nombre:<40} │ {s['total']:9,d} │ {s['ci_cifrados']:9,d} │ {s['saldo_cifrados']:10,d} │")

    t = sum(s["total"] for s in stats.values())
    tc = sum(s["ci_cifrados"] for s in stats.values())
    ts = sum(s["saldo_cifrados"] for s in stats.values())

    print("├──────┼────────────────────────────────────────┼───────────┼───────────┼────────────┤")
    print(f"│      │ {'TOTAL':<40} │ {t:9,d} │ {tc:9,d} │ {ts:10,d} │")
    print("└──────┴────────────────────────────────────────┴───────────┴───────────┴────────────┘")

    # Guardar stats JSON para validate.sh
    stats_path = os.path.join(output_dir, "stats.json")
    stats_str = {str(k): v for k, v in stats.items()}
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats_str, f, indent=2, ensure_ascii=False)

    # Guardar inconsistencias
    inconsistencias_path = os.path.join(output_dir, "inconsistencias.csv")
    with open(inconsistencias_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["fila", "motivo", "IdBanco", "NroCuenta", "Identificacion", "Saldo"],
        )
        writer.writeheader()
        writer.writerows(inconsistencias)

    print(f"\n✅ Archivos generados en: {output_dir}")
    print(f"📊 Estadísticas guardadas en: {stats_path}")
    print(f"📝 Inconsistencias guardadas en: {inconsistencias_path}")


# ── Generadores por motor ─────────────────────────────────────────────────────

def _escape_sql(val: str) -> str:
    """Escapa comillas simples para SQL."""
    return val.replace("'", "''")


def _gen_postgres(bid, cfg, registros, now_str, output_dir):
    db = cfg["db"]
    chunk_size = 1000
    chunks = [registros[i:i + chunk_size] for i in range(0, len(registros), chunk_size)]
    lines = [
        f"-- Generado por process_csv.py — {now_str}",
        f"-- Banco: {cfg['nombre']} (ID={bid}) | PostgreSQL | DB: {db}",
        f"\\c {db};",
        "",
    ]
    for chunk in chunks:
        rows = []
        for r in chunk:
            s = f"'{_escape_sql(r['saldo'])}'" if r["saldo_cifrado"] else r["saldo"]
            rows.append(
                f"  ('{_escape_sql(r['ci'])}', '{_escape_sql(r['nombres'])}', '{_escape_sql(r['apellidos'])}', "
                f"'{_escape_sql(r['nro_cuenta'])}', {r['banco_id']}, {s}, NULL, "
                f"{'TRUE' if r['ci_cifrado'] else 'FALSE'}, "
                f"{'TRUE' if r['saldo_cifrado'] else 'FALSE'}, "
                f"NULL, '{now_str}', 'seed_loader')"
            )
        lines.append(
            "INSERT INTO cuentas\n"
            "  (ci, nombres, apellidos, nro_cuenta, id_banco, saldo, saldo_bs,\n"
            "   ci_cifrado, saldo_cifrado, code_verif, created_at, created_user)\nVALUES\n"
            + ",\n".join(rows)
            + ";"
        )
        lines.append("")
    _write(output_dir, f"banco_{bid:02d}_{db}.sql", "\n".join(lines))


def _gen_mysql(bid, cfg, registros, now_str, output_dir):
    db = cfg["db"]
    chunk_size = 1000
    chunks = [registros[i:i + chunk_size] for i in range(0, len(registros), chunk_size)]
    lines = [
        f"-- Generado por process_csv.py — {now_str}",
        f"-- Banco: {cfg['nombre']} (ID={bid}) | MySQL/MariaDB | DB: {db}",
        f"USE {db};",
        "",
    ]
    for chunk in chunks:
        rows = []
        for r in chunk:
            s = f"'{_escape_sql(r['saldo'])}'"
            rows.append(
                f"  ('{_escape_sql(r['ci'])}', '{_escape_sql(r['nombres'])}', '{_escape_sql(r['apellidos'])}', "
                f"'{_escape_sql(r['nro_cuenta'])}', {r['banco_id']}, {s}, NULL, "
                f"{'1' if r['ci_cifrado'] else '0'}, "
                f"{'1' if r['saldo_cifrado'] else '0'}, "
                f"NULL, '{now_str}', 'seed_loader')"
            )
        lines.append(
            "INSERT INTO cuentas\n"
            "  (ci, nombres, apellidos, nro_cuenta, id_banco, saldo, saldo_bs,\n"
            "   ci_cifrado, saldo_cifrado, code_verif, created_at, created_user)\nVALUES\n"
            + ",\n".join(rows)
            + ";"
        )
        lines.append("")
    _write(output_dir, f"banco_{bid:02d}_{db}.sql", "\n".join(lines))


def _gen_mongo(bid, cfg, registros, now_str, output_dir):
    db = cfg["db"]
    banco_nombre = cfg["nombre"]
    chunk_size = 500
    chunks = [registros[i:i + chunk_size] for i in range(0, len(registros), chunk_size)]
    lines = [
        f"// Generado por process_csv.py — {now_str}",
        f"// Banco: {banco_nombre} (ID={bid}) | MongoDB | DB: {db}",
        f"db = db.getSiblingDB('{db}');",
        "",
    ]
    for chunk in chunks:
        docs = []
        for r in chunk:
            saldo_js = f'"{r["saldo"]}"'
            ci_flag = str(r["ci_cifrado"]).lower()
            sal_flag = str(r["saldo_cifrado"]).lower()
            nom = r["nombres"].replace('"', '\\"')
            ape = r["apellidos"].replace('"', '\\"')
            ci_v = r["ci"].replace('"', '\\"')
            nro_v = r["nro_cuenta"].replace('"', '\\"')
            docs.append(
                f'  {{ ci: "{ci_v}", nombres: "{nom}", apellidos: "{ape}",' 
                f' nro_cuenta: "{nro_v}", id_banco: {r["banco_id"]},'
                f' saldo: {saldo_js}, saldo_bs: null,'
                f' ci_cifrado: {ci_flag}, saldo_cifrado: {sal_flag},'
                f' code_verif: null, created_at: new Date("{now_str}"), created_user: "seed_loader",'
                f' updated_at: null, updated_user: null, deleted_at: null, deleted_user: null }}'
            )
        n = len(chunk)
        lines.append(f"db.cuentas.insertMany([\n" + ",\n".join(docs) + "\n]);")
        lines.append(f"print('✅ {banco_nombre} — chunk {n} docs insertados.');")
        lines.append("")
    _write(output_dir, f"banco_{bid:02d}_{db}.js", "\n".join(lines))


def _gen_redis(bid, cfg, registros, now_str, output_dir):
    banco_nombre = cfg["nombre"]
    lines = [
        "#!/bin/sh",
        f"# Generado por process_csv.py — {now_str}",
        f"# Banco: {banco_nombre} (ID={bid}) | Redis",
        f"# Total registros: {len(registros)}",
        "",
    ]
    for r in registros:
        key = "cuenta:" + r["nro_cuenta"]
        ci_flag = "1" if r["ci_cifrado"] else "0"
        sal_flag = "1" if r["saldo_cifrado"] else "0"
        cmd = (
            f'redis-cli -a admin123 --no-auth-warning HSET "{key}"'
            f' ci "{r["ci"]}" nombres "{r["nombres"]}" apellidos "{r["apellidos"]}"'
            f' nro_cuenta "{r["nro_cuenta"]}" id_banco "{r["banco_id"]}"'
            f' saldo "{r["saldo"]}" saldo_bs ""'
            f' ci_cifrado "{ci_flag}" saldo_cifrado "{sal_flag}"'
            f' code_verif "" created_at "{now_str}" created_user "seed_loader"'
        )
        lines.append(cmd)
    _write(output_dir, f"banco_{bid:02d}_redis.sh", "\n".join(lines) + "\n")


def _write(output_dir, filename, content):
    path = os.path.join(output_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✅ {filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Procesa CSV y genera inserts cifrados por banco")
    parser.add_argument("--csv", default=None, help="Ruta al CSV base")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)

    # Intentar primero el dataset nuevo, luego el original
    new_csv = os.path.join(project_dir, "data", "01 - Practica 2 Dataset.csv")
    orig_csv = os.path.join(project_dir, "data", "dataset_base.csv")

    if args.csv:
        csv_path = args.csv
    elif os.path.exists(new_csv):
        csv_path = new_csv
    else:
        csv_path = orig_csv

    output_dir = os.path.join(project_dir, "data", "processed")
    procesar(csv_path, output_dir)