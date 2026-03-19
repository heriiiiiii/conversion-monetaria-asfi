from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


import argparse
import asyncio
import json
from pathlib import Path

from app.clients.mock_bank_client import MockBankClient
from app.core.pipeline import AsfiProcessingPipeline
from app.crypto.key_registry import KeyRegistry
from app.exchange.rate_service import DynamicRateService
from app.repository.factory import get_repository


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ejecuta una demo end-to-end del bloque 3 ASFI.")
    parser.add_argument("--dataset", required=True, help="Ruta al CSV del dataset.")
    parser.add_argument("--limit", type=int, default=None, help="Límite de cuentas por banco.")
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--rate-mode", default="OFICIAL", choices=["OFICIAL", "REFERENCIAL"])
    parser.add_argument("--interval-seconds", type=int, default=3)
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    dataset_path = Path(args.dataset).resolve()
    if not dataset_path.exists():
        raise SystemExit(f"No se encontró el dataset: {dataset_path}")

    repository = get_repository()
    repository.truncate_all()
    key_registry = KeyRegistry()
    repository.seed_banks(key_registry.export_mapping())
    client = MockBankClient(dataset_path=dataset_path, key_registry=key_registry)
    rate_service = DynamicRateService(interval_seconds=args.interval_seconds)
    pipeline = AsfiProcessingPipeline(client=client, repository=repository, rate_service=rate_service)

    summary = await pipeline.process_all_banks(
        rate_mode=args.rate_mode,
        batch_size=args.batch_size,
        limit_per_bank=args.limit,
    )
    print(json.dumps(summary.model_dump(mode="json"), indent=2, ensure_ascii=False))
    if hasattr(repository, "db_path"):
        print(f"\nSQLite demo DB: {repository.db_path}")
    else:
        print("\nMySQL demo DB: ASFI_Central")
    print("Audit log: logs/audit.log")


if __name__ == "__main__":
    asyncio.run(main())