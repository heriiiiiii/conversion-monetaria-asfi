from __future__ import annotations

from app.core.schemas import CallbackResult, ConsistencyResult, ConversionRecord


class ConsistencyChecker:
    def validate(self, record: ConversionRecord, callback: CallbackResult) -> ConsistencyResult:
        consistent = (
            callback.accepted
            and callback.codigo_verificacion == record.codigo_verificacion
            and callback.saldo_bs == record.saldo_bs
        )
        detail = "Consistencia validada entre ASFI y banco." if consistent else "Diferencia detectada entre ASFI y banco."
        return ConsistencyResult(
            banco_id=record.banco_id,
            cuenta_id=record.cuenta_id,
            is_consistent=consistent,
            details=detail,
        )
