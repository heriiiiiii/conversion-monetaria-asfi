from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.audit.logger import AuditLogger
from app.clients.mock_bank_client import MockBankClient
from app.config import settings
from app.core.pipeline import AsfiProcessingPipeline
from app.exchange.rate_service import DynamicRateService
from app.repository.sqlite_repository import AsfiRepository
from app.crypto.key_registry import KeyRegistry


router = APIRouter(prefix="/api/v1")
_repository = AsfiRepository()
_rate_service = DynamicRateService()
_key_registry = KeyRegistry()
_client: MockBankClient | None = None
_pipeline: AsfiProcessingPipeline | None = None


def _get_pipeline() -> AsfiProcessingPipeline:
    global _client, _pipeline
    candidates = [
        settings.project_root.parent / '01 - Practica 2 Dataset.csv',
        settings.project_root.parent / 'datasets' / '01 - Practica 2 Dataset.csv',
        settings.project_root / 'data' / '01 - Practica 2 Dataset.csv',
    ]
    dataset = next((item for item in candidates if item.exists()), candidates[0])
    if _client is None:
        _client = MockBankClient(dataset_path=dataset, key_registry=_key_registry)
    if _pipeline is None:
        _repository.seed_banks(_key_registry.export_mapping())
        _pipeline = AsfiProcessingPipeline(client=_client, repository=_repository, rate_service=_rate_service)
    return _pipeline


@router.get("/exchange-rate/current")
def current_exchange_rate(mode: str = Query(default="OFICIAL")):
    return _rate_service.current_rate(mode).model_dump(mode="json")


@router.post("/process/all")
async def process_all(rate_mode: str = Query(default="OFICIAL"), batch_size: int = Query(default=500, ge=1), limit_per_bank: int | None = Query(default=None, ge=1)):
    pipeline = _get_pipeline()
    return (await pipeline.process_all_banks(rate_mode=rate_mode, batch_size=batch_size, limit_per_bank=limit_per_bank)).model_dump(mode="json")


@router.post("/process/bank/{bank_id}")
async def process_bank(bank_id: int, rate_mode: str = Query(default="OFICIAL"), batch_size: int = Query(default=500, ge=1), limit: int | None = Query(default=None, ge=1)):
    pipeline = _get_pipeline()
    return (await pipeline.process_bank(bank_id=bank_id, rate_mode=rate_mode, batch_size=batch_size, limit=limit)).model_dump(mode="json")


@router.get("/audit/recent")
def recent_audit(limit: int = Query(default=20, ge=1, le=100)):
    return {"items": _repository.fetch_recent_audit(limit=limit)}
