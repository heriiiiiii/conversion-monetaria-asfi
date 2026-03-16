from __future__ import annotations

import asyncio
from pathlib import Path
from typing import AsyncIterator

import httpx

from app.clients.bank_client import AbstractBankClient
from app.core.schemas import BankBatchResponse, CallbackResult


class HttpBankClient(AbstractBankClient):
    def __init__(self, endpoints: dict[int, dict], timeout_seconds: int = 20) -> None:
        self.endpoints = endpoints
        self.timeout_seconds = timeout_seconds

    async def fetch_bank_batches(self, bank_id: int, batch_size: int = 500, limit: int | None = None) -> AsyncIterator[BankBatchResponse]:
        cfg = self.endpoints[bank_id]
        params = {"batch_size": batch_size}
        if limit:
            params["limit"] = limit
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.get(
                cfg["read_url"],
                params=params,
                auth=(cfg.get("username", ""), cfg.get("password", "")),
            )
            response.raise_for_status()
            data = response.json()
            for batch in data["batches"]:
                yield BankBatchResponse(**batch)

    async def send_callback(self, callback: CallbackResult) -> CallbackResult:
        cfg = self.endpoints[callback.banco_id]
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(
                cfg["callback_url"],
                json=callback.model_dump(mode="json"),
                auth=(cfg.get("username", ""), cfg.get("password", "")),
            )
            response.raise_for_status()
        return callback
