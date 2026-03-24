from __future__ import annotations

import hashlib
import json
import secrets
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from typing import Iterable

from app.core.schemas import BankAccountPayload


class NonceStore:
    def __init__(self, ttl_seconds: int = 300) -> None:
        self.ttl_seconds = ttl_seconds
        self._values: OrderedDict[str, datetime] = OrderedDict()

    def _purge(self) -> None:
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(seconds=self.ttl_seconds)
        expired = [key for key, value in self._values.items() if value < cutoff]
        for key in expired:
            self._values.pop(key, None)

    def seen(self, nonce: str) -> bool:
        self._purge()
        return nonce in self._values

    def register(self, nonce: str) -> None:
        self._purge()
        self._values[nonce] = datetime.now(timezone.utc)


def generate_nonce(size: int = 16) -> str:
    return secrets.token_hex(size)


def generate_verification_code() -> str:
    return secrets.token_hex(4).upper()


def derive_bank_api_key(bank_id: int) -> str:
    return hashlib.sha256(f"ASFI|BANK|{bank_id}|APIKEY".encode("utf-8")).hexdigest()[:32].upper()


_ALLOWED_BATCH_FIELDS = (
    "banco_id",
    "banco_nombre",
    "algoritmo",
    "cuenta_id",
    "identificacion",
    "nombres",
    "apellidos",
    "nro_cuenta",
    "saldo_usd",
    "campos_cifrados",
    "timestamp",
    "nonce",
    "lote_id",
)


def compute_batch_hash(bank_id: int, lote_id: str, timestamp: str, nonce: str, cuentas: Iterable[BankAccountPayload]) -> str:
    normalized = []
    for account in cuentas:
        payload = account.model_dump(mode="json", include=set(_ALLOWED_BATCH_FIELDS))
        normalized.append(payload)
    body = {
        "bank_id": bank_id,
        "lote_id": lote_id,
        "timestamp": timestamp,
        "nonce": nonce,
        "cuentas": sorted(normalized, key=lambda item: item["cuenta_id"]),
    }
    raw = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
