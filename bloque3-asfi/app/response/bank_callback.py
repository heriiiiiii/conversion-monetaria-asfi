from __future__ import annotations

from app.clients.bank_client import AbstractBankClient
from app.core.schemas import CallbackResult, ConversionRecord


class BankCallbackService:
    def __init__(self, client: AbstractBankClient) -> None:
        self.client = client

    async def send_result(self, record: ConversionRecord) -> CallbackResult:
        callback = CallbackResult(
            banco_id=record.banco_id,
            cuenta_id=record.cuenta_id,
            accepted=True,
            saldo_bs=record.saldo_bs,
            codigo_verificacion=record.codigo_verificacion,
        )
        return await self.client.send_callback(callback)
