from __future__ import annotations

from datetime import datetime, timezone

from app.config import settings
from app.core.schemas import BankBatchResponse
from app.utils.security import NonceStore


class RequestValidator:
    def __init__(self, nonce_store: NonceStore | None = None) -> None:
        self.nonce_store = nonce_store or NonceStore(settings.nonce_ttl_seconds)

    def validate_batch(self, batch: BankBatchResponse) -> None:
        if not batch.cuentas:
            raise ValueError("El lote recibido no contiene cuentas.")
        self._validate_timestamp(batch.timestamp)
        self._validate_nonce(batch.nonce)
        if batch.banco_id <= 0:
            raise ValueError("BancoId inválido.")
        if not batch.algoritmo:
            raise ValueError("El lote no informa algoritmo.")

    def _validate_timestamp(self, timestamp: str) -> None:
        received_at = datetime.fromisoformat(timestamp)
        now = datetime.now(timezone.utc)
        diff = abs((now - received_at).total_seconds())
        if diff > settings.nonce_ttl_seconds:
            raise ValueError("Timestamp fuera de la ventana permitida.")

    def _validate_nonce(self, nonce: str) -> None:
        if self.nonce_store.seen(nonce):
            raise ValueError("Nonce repetido: posible replay attack.")
        self.nonce_store.register(nonce)
