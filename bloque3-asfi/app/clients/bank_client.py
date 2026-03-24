from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator

from app.core.schemas import BankBatchResponse, CallbackResult


class AbstractBankClient(ABC):
    @abstractmethod
    async def fetch_bank_batches(self, bank_id: int, batch_size: int = 500, limit: int | None = None) -> AsyncIterator[BankBatchResponse]:
        raise NotImplementedError

    @abstractmethod
    async def send_callback(self, callback: CallbackResult) -> CallbackResult:
        raise NotImplementedError
