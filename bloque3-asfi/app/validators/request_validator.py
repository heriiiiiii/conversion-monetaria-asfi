from __future__ import annotations

from datetime import datetime, timezone

from app.config import settings
from app.core.schemas import BankBatchResponse
from app.utils.security import NonceStore, compute_batch_hash, derive_bank_api_key


class RequestValidator:
    def __init__(self, nonce_store: NonceStore | None = None) -> None:
        self.nonce_store = nonce_store or NonceStore(settings.nonce_ttl_seconds)

    def validate_batch(self, batch: BankBatchResponse) -> None:
        if not batch.cuentas:
            raise ValueError("El lote recibido no contiene cuentas.")

        self._validate_bank(batch)

        if batch.timestamp:
            self._validate_timestamp(batch.timestamp)

        if batch.nonce:
            self._validate_nonce(batch.nonce)

        if batch.api_key:
            self._validate_api_key(batch)

        if batch.request_hash:
            self._validate_integrity(batch)

    def _validate_bank(self, batch: BankBatchResponse) -> None:
        if batch.banco_id <= 0:
            raise ValueError("BancoId inválido.")

        if not batch.algoritmo:
            raise ValueError("El lote no informa algoritmo.")

        for account in batch.cuentas:
            if account.banco_id != batch.banco_id:
                raise ValueError("El lote contiene cuentas de otro banco.")

            if account.lote_id != batch.lote_id:
                raise ValueError("El lote contiene cuentas con lote_id inconsistente.")

            if not account.cuenta_id:
                raise ValueError("El lote contiene una cuenta sin CuentaId.")

    def _validate_timestamp(self, timestamp: str) -> None:
        received_at = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        if received_at.tzinfo is None:
            received_at = received_at.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        diff = abs((now - received_at).total_seconds())
        if diff > settings.nonce_ttl_seconds:
            raise ValueError("Timestamp fuera de la ventana permitida.")

    def _validate_nonce(self, nonce: str) -> None:
        if self.nonce_store.seen(nonce):
            raise ValueError("Nonce repetido: posible replay attack.")
        self.nonce_store.register(nonce)

    def _validate_api_key(self, batch: BankBatchResponse) -> None:
        expected = derive_bank_api_key(batch.banco_id)
        if batch.api_key != expected:
            raise ValueError("API key inválida para el banco emisor.")

    def _validate_integrity(self, batch: BankBatchResponse) -> None:
        expected_hash = compute_batch_hash(
            bank_id=batch.banco_id,
            lote_id=batch.lote_id,
            timestamp=batch.timestamp,
            nonce=batch.nonce,
            cuentas=batch.cuentas,
        )
        if batch.request_hash != expected_hash:
            raise ValueError("Hash de integridad inválido: posible manipulación del payload.")