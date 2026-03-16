from __future__ import annotations

import asyncio
from decimal import Decimal
from typing import Iterable

from app.audit.logger import AuditLogger
from app.clients.bank_client import AbstractBankClient
from app.constants import BANK_BY_ID, BANK_CATALOG
from app.consistency.checker import ConsistencyChecker
from app.converter.currency import convert_usd_to_bs
from app.core.schemas import BankProcessingSummary, ConversionRecord, DecryptedAccountRecord, ProcessingError, RunSummary
from app.crypto.decryptor import DecryptorService
from app.crypto.encrypted_fields import EncryptedFieldsInterpreter
from app.exchange.rate_service import DynamicRateService
from app.repository.sqlite_repository import AsfiRepository
from app.response.bank_callback import BankCallbackService
from app.utils.security import generate_verification_code
from app.utils.time_utils import utcnow_iso
from app.validators.request_validator import RequestValidator


class AsfiProcessingPipeline:
    def __init__(
        self,
        client: AbstractBankClient,
        repository: AsfiRepository,
        rate_service: DynamicRateService,
        validator: RequestValidator | None = None,
        decryptor: DecryptorService | None = None,
        interpreter: EncryptedFieldsInterpreter | None = None,
        audit_logger: AuditLogger | None = None,
    ) -> None:
        self.client = client
        self.repository = repository
        self.rate_service = rate_service
        self.validator = validator or RequestValidator()
        self.decryptor = decryptor or DecryptorService()
        self.interpreter = interpreter or EncryptedFieldsInterpreter()
        self.audit_logger = audit_logger or AuditLogger()
        self.callback_service = BankCallbackService(client)
        self.consistency_checker = ConsistencyChecker()

    async def process_all_banks(self, rate_mode: str = "OFICIAL", batch_size: int = 500, limit_per_bank: int | None = None, bank_ids: Iterable[int] | None = None) -> RunSummary:
        started_at = utcnow_iso()
        ids = list(bank_ids) if bank_ids else [item["bank_id"] for item in BANK_CATALOG]
        summaries = await asyncio.gather(
            *(self.process_bank(bank_id, rate_mode=rate_mode, batch_size=batch_size, limit=limit_per_bank) for bank_id in ids)
        )
        finished_at = utcnow_iso()
        total_accounts = sum(item.processed_accounts for item in summaries)
        total_successful = sum(item.successful_accounts for item in summaries)
        total_failed = sum(item.failed_accounts for item in summaries)
        return RunSummary(
            total_banks=len(ids),
            total_accounts=total_accounts,
            total_successful=total_successful,
            total_failed=total_failed,
            started_at=started_at,
            finished_at=finished_at,
            bank_summaries=summaries,
        )

    async def process_bank(self, bank_id: int, rate_mode: str = "OFICIAL", batch_size: int = 500, limit: int | None = None) -> BankProcessingSummary:
        bank = BANK_BY_ID[bank_id]
        summary = BankProcessingSummary(
            banco_id=bank_id,
            banco_nombre=bank["name"],
            algoritmo=bank["algorithm"],
            started_at=utcnow_iso(),
        )
        async for batch in self.client.fetch_bank_batches(bank_id=bank_id, batch_size=batch_size, limit=limit):
            try:
                self.validator.validate_batch(batch)
                quote = self.rate_service.current_rate(rate_mode)
                self.repository.log_rate(quote)
                self.repository.log_audit(quote.generated_at, bank_id, None, "rate_quote", f"Tipo de cambio {quote.rate}", str(quote.rate), quote.mode, batch.lote_id)
                self.audit_logger.write({
                    "timestamp": quote.generated_at,
                    "bank_id": bank_id,
                    "event": "rate_quote",
                    "exchange_rate": str(quote.rate),
                    "mode": quote.mode,
                    "slot": quote.slot,
                    "batch_id": batch.lote_id,
                })
                summary.batches_processed += 1
            except Exception as exc:
                err = ProcessingError(banco_id=bank_id, cuenta_id=None, stage="validacion_lote", error=str(exc), lote_id=batch.lote_id)
                summary.errors.append(err)
                summary.failed_accounts += len(batch.cuentas)
                self.repository.log_error(err)
                continue

            for account in batch.cuentas:
                summary.processed_accounts += 1
                try:
                    encrypted_fields = self.interpreter.resolve(account.campos_cifrados)
                    decrypted = self.decryptor.decrypt_fields(bank_id, batch.algoritmo, account.model_dump(), encrypted_fields)
                    record = DecryptedAccountRecord(
                        banco_id=bank_id,
                        banco_nombre=bank["name"],
                        algoritmo=batch.algoritmo,
                        cuenta_id=account.cuenta_id,
                        identificacion=str(decrypted["identificacion"]),
                        nombres=str(decrypted["nombres"]),
                        apellidos=str(decrypted["apellidos"]),
                        nro_cuenta=str(decrypted["nro_cuenta"]),
                        saldo_usd=Decimal(decrypted["saldo_usd"]),
                        campos_cifrados=account.campos_cifrados,
                        lote_id=batch.lote_id,
                    )
                    saldo_bs = convert_usd_to_bs(record.saldo_usd, quote.rate)
                    conversion = ConversionRecord(
                        cuenta_id=record.cuenta_id,
                        banco_id=bank_id,
                        banco_nombre=bank["name"],
                        saldo_usd=record.saldo_usd,
                        saldo_bs=saldo_bs,
                        fecha_conversion=utcnow_iso(),
                        codigo_verificacion=generate_verification_code(),
                        tipo_cambio=quote.rate,
                        modo_tipo_cambio=quote.mode,
                        lote_id=batch.lote_id,
                        identificacion=record.identificacion,
                        nro_cuenta=record.nro_cuenta,
                    )
                    self.repository.save_conversion(conversion)
                    self.repository.log_audit(conversion.fecha_conversion, bank_id, record.cuenta_id, "conversion", f"Conversión {record.saldo_usd} USD -> {saldo_bs} Bs.", str(quote.rate), quote.mode, batch.lote_id)
                    self.audit_logger.write({
                        "timestamp": conversion.fecha_conversion,
                        "bank_id": bank_id,
                        "account_id": record.cuenta_id,
                        "event": "conversion",
                        "amount_usd": str(record.saldo_usd),
                        "amount_bs": str(saldo_bs),
                        "exchange_rate": str(quote.rate),
                        "mode": quote.mode,
                        "verification_code": conversion.codigo_verificacion,
                        "batch_id": batch.lote_id,
                    })
                    callback = await self.callback_service.send_result(conversion)
                    self.repository.save_callback(callback)
                    consistency = self.consistency_checker.validate(conversion, callback)
                    self.repository.save_consistency(consistency)
                    summary.successful_accounts += 1
                except Exception as exc:
                    err = ProcessingError(
                        banco_id=bank_id,
                        cuenta_id=account.cuenta_id,
                        stage="procesamiento_cuenta",
                        error=str(exc),
                        lote_id=batch.lote_id,
                    )
                    summary.failed_accounts += 1
                    summary.errors.append(err)
                    self.repository.log_error(err)
                    self.repository.log_audit(utcnow_iso(), bank_id, account.cuenta_id, "error", str(exc), lote_id=batch.lote_id)
        summary.finished_at = utcnow_iso()
        return summary
