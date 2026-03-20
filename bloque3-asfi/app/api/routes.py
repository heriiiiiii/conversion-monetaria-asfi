from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, Query

from app.clients.bank_client import AbstractBankClient
from app.clients.http_bank_client import HttpBankClient
from app.clients.mock_bank_client import MockBankClient
from app.config import settings
from app.core.pipeline import AsfiProcessingPipeline
from app.exchange.rate_service import DynamicRateService
from app.repository.factory import get_repository
from app.crypto.key_registry import KeyRegistry


router = APIRouter(prefix="/api/v1")
_repository = get_repository()
_rate_service = DynamicRateService()
_key_registry = KeyRegistry()
_client: AbstractBankClient | None = None
_pipeline: AsfiProcessingPipeline | None = None


def _build_http_endpoints() -> dict[int, dict]:
    use_docker_names = os.getenv("ASFI_BANK_API_USE_DOCKER_NAMES", "false").lower() == "true"
    key_map = {item["bank_id"]: item for item in _key_registry.export_mapping()}

    endpoints: dict[int, dict] = {}
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


def _build_mock_client() -> MockBankClient:
    candidates = [
        settings.project_root.parent / "01 - Practica 2 Dataset.csv",
        settings.project_root.parent / "datasets" / "01 - Practica 2 Dataset.csv",
        settings.project_root / "data" / "01 - Practica 2 Dataset.csv",
        Path(r"C:\dataset2\01 - Practica 2 Dataset.csv"),
    ]
    dataset = next((item for item in candidates if item.exists()), candidates[0])
    return MockBankClient(dataset_path=dataset, key_registry=_key_registry)


def _build_client() -> AbstractBankClient:
    client_mode = os.getenv("ASFI_BANK_CLIENT_MODE", "http").lower()

    if client_mode == "mock":
        return _build_mock_client()

    return HttpBankClient(
        endpoints=_build_http_endpoints(),
        timeout_seconds=settings.bank_timeout_seconds,
    )


def _get_pipeline() -> AsfiProcessingPipeline:
    global _client, _pipeline

    if _client is None:
        _client = _build_client()

    if _pipeline is None:
        _repository.seed_banks(_key_registry.export_mapping())
        _pipeline = AsfiProcessingPipeline(
            client=_client,
            repository=_repository,
            rate_service=_rate_service,
        )

    return _pipeline


@router.get("/exchange-rate/current")
def current_exchange_rate(mode: str = Query(default="OFICIAL")):
    return _rate_service.current_rate(mode).model_dump(mode="json")


@router.post("/process/all")
async def process_all(
    rate_mode: str = Query(default="OFICIAL"),
    batch_size: int = Query(default=500, ge=1),
    limit_per_bank: int | None = Query(default=None, ge=1),
):
    pipeline = _get_pipeline()
    return (
        await pipeline.process_all_banks(
            rate_mode=rate_mode,
            batch_size=batch_size,
            limit_per_bank=limit_per_bank,
        )
    ).model_dump(mode="json")


@router.post("/process/bank/{bank_id}")
async def process_bank(
    bank_id: int,
    rate_mode: str = Query(default="OFICIAL"),
    batch_size: int = Query(default=500, ge=1),
    limit: int | None = Query(default=None, ge=1),
):
    pipeline = _get_pipeline()
    return (
        await pipeline.process_bank(
            bank_id=bank_id,
            rate_mode=rate_mode,
            batch_size=batch_size,
            limit=limit,
        )
    ).model_dump(mode="json")


@router.get("/audit/recent")
def recent_audit(limit: int = Query(default=20, ge=1, le=100)):
    return {"items": _repository.fetch_recent_audit(limit=limit)}