from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import asyncio
import json
import os
from pathlib import Path
from typing import Any

from app.clients.bank_client import AbstractBankClient
from app.clients.http_bank_client import HttpBankClient
from app.clients.mock_bank_client import MockBankClient
from app.config import settings
from app.core.pipeline import AsfiProcessingPipeline
from app.crypto.key_registry import KeyRegistry
from app.exchange.rate_service import DynamicRateService
from app.repository.factory import get_repository


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ejecuta una prueba end-to-end del bloque 3 ASFI.")
    parser.add_argument("--client-mode", choices=["http", "mock"], default=os.getenv("ASFI_BANK_CLIENT_MODE", "http"))
    parser.add_argument("--dataset", required=False, help="Ruta al CSV del dataset, solo para modo mock.")
    parser.add_argument("--limit", type=int, default=None, help="Límite de cuentas por banco.")
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--rate-mode", default="OFICIAL", choices=["OFICIAL", "REFERENCIAL"])
    parser.add_argument("--interval-seconds", type=int, default=3)
    parser.add_argument("--bank-id", type=int, default=None, help="Procesar solo un banco específico.")
    return parser.parse_args()


def _build_http_endpoints(key_registry: KeyRegistry) -> dict[int, dict[str, Any]]:
    use_docker_names = os.getenv("ASFI_BANK_API_USE_DOCKER_NAMES", "false").lower() == "true"
    key_map = {item["bank_id"]: item for item in key_registry.export_mapping()}

    endpoints: dict[int, dict[str, Any]] = {}
    for bank_id in range(1, 15):
        default_host = f"banco_api_{bank_id}" if use_docker_names else "localhost"
        host = os.getenv(f"ASFI_BANK_{bank_id}_HOST", default_host)
        port = int(os.getenv(f"ASFI_BANK_{bank_id}_PORT", str(8000 + bank_id)))

        bank_meta = key_map.get(bank_id, {})
        endpoints[bank_id] = {
            "read_url": f"http://{host}:{port}/api/cuentas",
            "callback_url": f"http://{host}:{port}/api/cuentas/{{cuenta_id}}/actualizar-saldo",
            "health_url": f"http://{host}:{port}/api/health",
            "config_url": f"http://{host}:{port}/api/configuracion",
            "bank_name": bank_meta.get("name", f"Banco {bank_id}"),
            "algorithm": bank_meta.get("algorithm", "DESCONOCIDO"),
        }

    return endpoints


def _build_mock_client(args: argparse.Namespace, key_registry: KeyRegistry) -> MockBankClient:
    if not args.dataset:
        raise SystemExit("En modo mock debes enviar --dataset")

    dataset_path = Path(args.dataset).resolve()
    if not dataset_path.exists():
        raise SystemExit(f"No se encontró el dataset: {dataset_path}")

    return MockBankClient(dataset_path=dataset_path, key_registry=key_registry)


def _build_client(args: argparse.Namespace, key_registry: KeyRegistry) -> AbstractBankClient:
    if args.client_mode == "mock":
        return _build_mock_client(args, key_registry)

    return HttpBankClient(
        endpoints=_build_http_endpoints(key_registry),
        timeout_seconds=settings.bank_timeout_seconds,
    )


async def main() -> None:
    args = parse_args()

    repository = get_repository()
    repository.truncate_all()

    key_registry = KeyRegistry()
    repository.seed_banks(key_registry.export_mapping())

    client = _build_client(args, key_registry)
    rate_service = DynamicRateService(interval_seconds=args.interval_seconds)
    pipeline = AsfiProcessingPipeline(client=client, repository=repository, rate_service=rate_service)

    if args.bank_id is not None:
        summary = await pipeline.process_bank(
            bank_id=args.bank_id,
            rate_mode=args.rate_mode,
            batch_size=args.batch_size,
            limit=args.limit,
        )
        print(json.dumps(summary.model_dump(mode="json"), indent=2, ensure_ascii=False))
    else:
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

    print(f"Client mode: {args.client_mode}")
    print("Audit log: logs/audit.log")


if __name__ == "__main__":
    asyncio.run(main())