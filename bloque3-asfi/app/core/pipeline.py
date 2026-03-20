from __future__ import annotations

import asyncio
from decimal import Decimal
from typing import Any, Iterable

from app.audit.logger import AuditLogger
from app.clients.bank_client import AbstractBankClient
from app.constants import BANK_BY_ID, BANK_CATALOG
from app.consistency.checker import ConsistencyChecker
from app.converter.currency import convert_usd_to_bs
from app.core.schemas import (
    AuditEvent,
    BankProcessingSummary,
    ConversionRecord,
    DecryptedAccountRecord,
    ProcessingError,
    RunSummary,
)
from app.crypto.decryptor import DecryptorService
from app.crypto.encrypted_fields import EncryptedFieldsInterpreter
from app.exchange.rate_service import DynamicRateService
from app.response.bank_callback import BankCallbackService
from app.utils.security import generate_verification_code
from app.utils.time_utils import utcnow_iso
from app.validators.request_validator import RequestValidator


class AsfiProcessingPipeline:
    def __init__(
        self,
        client: AbstractBankClient,
        repository: Any,
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

    async def process_all_banks(
        self,
        rate_mode: str = "OFICIAL",
        batch_size: int = 500,
        limit_per_bank: int | None = None,
        bank_ids: Iterable[int] | None = None,
    ) -> RunSummary:
        started_at = utcnow_iso()
        ids = list(bank_ids) if bank_ids else [item["bank_id"] for item in BANK_CATALOG]

        summaries = await asyncio.gather(
            *(
                self.process_bank(
                    bank_id,
                    rate_mode=rate_mode,
                    batch_size=batch_size,
                    limit=limit_per_bank,
                )
                for bank_id in ids
            )
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

    async def process_bank(
        self,
        bank_id: int,
        rate_mode: str = "OFICIAL",
        batch_size: int = 500,
        limit: int | None = None,
    ) -> BankProcessingSummary:
        bank = BANK_BY_ID[bank_id]

        summary = BankProcessingSummary(
            banco_id=bank_id,
            banco_nombre=bank["name"],
            algoritmo=bank["algorithm"],
            started_at=utcnow_iso(),
        )

        async for batch in self.client.fetch_bank_batches(bank_id=bank_id, batch_size=batch_size, limit=limit):
            batch_audits: list[AuditEvent] = []
            batch_conversions: list[ConversionRecord] = []
            batch_callbacks = []
            batch_consistency = []
            batch_errors: list[ProcessingError] = []

            # si el cliente real trae metadata mejor que la del catálogo, la usamos
            summary.banco_nombre = batch.banco_nombre or summary.banco_nombre
            summary.algoritmo = batch.algoritmo or summary.algoritmo

            try:
                self.validator.validate_batch(batch)
                quote = self.rate_service.current_rate(rate_mode)
                self.repository.log_rate(quote)

                batch_audits.append(
                    AuditEvent(
                        timestamp=quote.generated_at,
                        banco_id=bank_id,
                        cuenta_id=None,
                        evento="rate_quote",
                        detalle=f"Tipo de cambio {quote.rate}",
                        tipo_cambio=str(quote.rate),
                        modo_tipo_cambio=quote.mode,
                        fuente_tipo_cambio=quote.source,
                        lote_id=batch.lote_id,
                    )
                )

                self.audit_logger.write(
                    {
                        "timestamp": quote.generated_at,
                        "bank_id": bank_id,
                        "event": "rate_quote",
                        "exchange_rate": str(quote.rate),
                        "mode": quote.mode,
                        "source": quote.source,
                        "slot": quote.slot,
                        "batch_id": batch.lote_id,
                    }
                )

                summary.batches_processed += 1

            except Exception as exc:
                err = ProcessingError(
                    banco_id=bank_id,
                    cuenta_id=None,
                    stage="validacion_lote",
                    error=str(exc),
                    lote_id=batch.lote_id,
                )
                summary.errors.append(err)
                summary.failed_accounts += len(batch.cuentas)
                self.repository.log_error(err)
                self.repository.log_audit(
                    utcnow_iso(),
                    bank_id,
                    None,
                    "error",
                    str(exc),
                    lote_id=batch.lote_id,
                )
                continue

            for account in batch.cuentas:
                summary.processed_accounts += 1

                try:
                    encrypted_fields = self.interpreter.resolve(account.campos_cifrados)
                    decrypted = self.decryptor.decrypt_fields(
                        bank_id,
                        batch.algoritmo,
                        account.model_dump(),
                        encrypted_fields,
                    )

                    record = DecryptedAccountRecord(
                        banco_id=bank_id,
                        banco_nombre=batch.banco_nombre or bank["name"],
                        algoritmo=batch.algoritmo or bank["algorithm"],
                        cuenta_id=account.cuenta_id,
                        identificacion=str(decrypted["identificacion"]),
                        nombres=str(decrypted["nombres"]),
                        apellidos=str(decrypted["apellidos"]),
                        nro_cuenta=str(decrypted["nro_cuenta"]),
                        saldo_usd=Decimal(str(decrypted["saldo_usd"])),
                        campos_cifrados=account.campos_cifrados,
                        lote_id=batch.lote_id,
                    )

                    saldo_bs = convert_usd_to_bs(record.saldo_usd, quote.rate)

                    conversion = ConversionRecord(
                        cuenta_id=record.cuenta_id,
                        banco_id=bank_id,
                        banco_nombre=record.banco_nombre,
                        saldo_usd=record.saldo_usd,
                        saldo_bs=saldo_bs,
                        fecha_conversion=utcnow_iso(),
                        codigo_verificacion=generate_verification_code(),
                        tipo_cambio=quote.rate,
                        modo_tipo_cambio=quote.mode,
                        fuente_tipo_cambio=quote.source,
                        lote_id=batch.lote_id,
                        identificacion=str(record.identificacion) if record.identificacion is not None else None,
                        nro_cuenta=record.nro_cuenta,
                    )

                    batch_conversions.append(conversion)

                    batch_audits.append(
                        AuditEvent(
                            timestamp=conversion.fecha_conversion,
                            banco_id=bank_id,
                            cuenta_id=record.cuenta_id,
                            evento="conversion",
                            detalle=f"Conversión {record.saldo_usd} USD -> {saldo_bs} Bs.",
                            tipo_cambio=str(quote.rate),
                            modo_tipo_cambio=quote.mode,
                            fuente_tipo_cambio=quote.source,
                            lote_id=batch.lote_id,
                        )
                    )

                    self.audit_logger.write(
                        {
                            "timestamp": conversion.fecha_conversion,
                            "bank_id": bank_id,
                            "account_id": record.cuenta_id,
                            "event": "conversion",
                            "amount_usd": str(record.saldo_usd),
                            "amount_bs": str(saldo_bs),
                            "exchange_rate": str(quote.rate),
                            "mode": quote.mode,
                            "source": quote.source,
                            "verification_code": conversion.codigo_verificacion,
                            "batch_id": batch.lote_id,
                        }
                    )

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
                    batch_errors.append(err)
                    batch_audits.append(
                        AuditEvent(
                            timestamp=utcnow_iso(),
                            banco_id=bank_id,
                            cuenta_id=account.cuenta_id,
                            evento="error",
                            detalle=str(exc),
                            lote_id=batch.lote_id,
                        )
                    )

            if batch_conversions:
                self.repository.save_conversions_batch(batch_conversions)

                callbacks = await asyncio.gather(
                    *(self.callback_service.send_result(item) for item in batch_conversions),
                    return_exceptions=True,
                )

                for conversion, callback_result in zip(batch_conversions, callbacks, strict=True):
                    if isinstance(callback_result, Exception):
                        err = ProcessingError(
                            banco_id=conversion.banco_id,
                            cuenta_id=conversion.cuenta_id,
                            stage="callback_banco",
                            error=str(callback_result),
                            lote_id=conversion.lote_id,
                        )
                        batch_errors.append(err)
                        summary.failed_accounts += 1
                        summary.successful_accounts = max(0, summary.successful_accounts - 1)
                        summary.errors.append(err)
                        batch_audits.append(
                            AuditEvent(
                                timestamp=utcnow_iso(),
                                banco_id=conversion.banco_id,
                                cuenta_id=conversion.cuenta_id,
                                evento="error",
                                detalle=str(callback_result),
                                lote_id=conversion.lote_id,
                            )
                        )
                        continue

                    batch_callbacks.append(callback_result)

                    asfi_record = self.repository.fetch_account(conversion.cuenta_id, conversion.banco_id)
                    consistency = self.consistency_checker.validate(conversion, callback_result, asfi_record)
                    batch_consistency.append(consistency)
                    summary.successful_accounts += 1

                self.repository.save_callbacks_batch(batch_callbacks)
                self.repository.save_consistency_batch(batch_consistency)

            if batch_audits:
                self.repository.log_audit_batch(batch_audits)

            if batch_errors:
                self.repository.log_errors_batch(batch_errors)

        summary.finished_at = utcnow_iso()
        return summary