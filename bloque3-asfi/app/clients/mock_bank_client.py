from __future__ import annotations

import asyncio
import math
from pathlib import Path
from typing import AsyncIterator

import pandas as pd

from app.clients.bank_client import AbstractBankClient
from app.config import settings
from app.constants import BANK_BY_ID
from app.core.schemas import BankAccountPayload, BankBatchResponse, CallbackResult
from app.crypto.algorithms import encrypt_text
from app.crypto.key_registry import KeyRegistry
from app.utils.security import compute_batch_hash, derive_bank_api_key, generate_nonce
from app.utils.time_utils import utcnow_iso


class MockBankClient(AbstractBankClient):
    def __init__(self, dataset_path: str | Path, key_registry: KeyRegistry | None = None) -> None:
        self.dataset_path = Path(dataset_path)
        self.key_registry = key_registry or KeyRegistry()
        self.df = pd.read_csv(self.dataset_path)
        self.callbacks: list[dict] = []

    async def fetch_bank_batches(self, bank_id: int, batch_size: int = 500, limit: int | None = None) -> AsyncIterator[BankBatchResponse]:
        await asyncio.sleep(0)
        bank = BANK_BY_ID[bank_id]
        material = self.key_registry.get(bank_id)
        subset = self.df[self.df["IdBanco"] == bank_id].copy()
        if limit:
            subset = subset.head(limit)
        total = len(subset)
        total_batches = max(1, math.ceil(total / batch_size))
        for batch_index in range(total_batches):
            chunk = subset.iloc[batch_index * batch_size : (batch_index + 1) * batch_size]
            records = []
            lote_id = f"BANK-{bank_id}-BATCH-{batch_index + 1}"
            batch_nonce = generate_nonce()
            batch_timestamp = utcnow_iso()
            for row in chunk.itertuples(index=False):
                campos_cifrados = []
                saldo_plain = f"{row.Saldo:.4f}"
                saldo_payload = encrypt_text(bank["algorithm"], saldo_plain, material)
                campos_cifrados.append("saldo_usd")

                ident_plain = str(row.Identificacion)
                if float(row.Saldo) >= float(settings.encrypt_large_amount_threshold):
                    ident_payload = encrypt_text(bank["algorithm"], ident_plain, material)
                    campos_cifrados.append("identificacion")
                else:
                    ident_payload = ident_plain

                record = BankAccountPayload(
                    banco_id=bank_id,
                    banco_nombre=bank["name"],
                    algoritmo=bank["algorithm"],
                    cuenta_id=int(row.NroCuenta),
                    identificacion=ident_payload,
                    nombres=str(row.Nombres),
                    apellidos=str(row.Apellidos),
                    nro_cuenta=str(row.NroCuenta),
                    saldo_usd=saldo_payload,
                    campos_cifrados=campos_cifrados,
                    timestamp=batch_timestamp,
                    nonce=batch_nonce,
                    lote_id=lote_id,
                )
                records.append(record)
            yield BankBatchResponse(
                banco_id=bank_id,
                banco_nombre=bank["name"],
                algoritmo=bank["algorithm"],
                lote_id=lote_id,
                timestamp=batch_timestamp,
                nonce=batch_nonce,
                cuentas=records,
                api_key=derive_bank_api_key(bank_id),
                request_hash=compute_batch_hash(bank_id, lote_id, batch_timestamp, batch_nonce, records),
            )

    async def send_callback(self, callback: CallbackResult) -> CallbackResult:
        await asyncio.sleep(0)
        self.callbacks.append(callback.model_dump())
        return callback
