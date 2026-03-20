from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from app.core.schemas import CallbackResult, ConsistencyResult, ConversionRecord


def _normalize_decimal(value: Any) -> str:
    if value is None:
        return ""
    try:
        return format(Decimal(str(value)), "f")
    except (InvalidOperation, ValueError, TypeError):
        return str(value)


class ConsistencyChecker:
    def validate(
        self,
        record: ConversionRecord,
        callback: CallbackResult,
        asfi_record: dict[str, Any] | None = None,
    ) -> ConsistencyResult:
        exists_in_asfi = asfi_record is not None

        asfi_saldo_matches = (
            exists_in_asfi
            and _normalize_decimal(asfi_record.get("SaldoBs")) == _normalize_decimal(record.saldo_bs)
        )

        asfi_code_matches = (
            exists_in_asfi
            and str(asfi_record.get("CodigoVerificacion")) == str(record.codigo_verificacion)
        )

        bank_matches = (
            callback.accepted
            and str(callback.codigo_verificacion) == str(record.codigo_verificacion)
            and _normalize_decimal(callback.saldo_bs) == _normalize_decimal(record.saldo_bs)
        )

        consistent = bool(exists_in_asfi and asfi_saldo_matches and asfi_code_matches and bank_matches)

        details = (
            "Consistencia validada entre ASFI y banco."
            if consistent
            else (
                f"exists_in_asfi={exists_in_asfi}; "
                f"asfi_saldo_matches={asfi_saldo_matches}; "
                f"asfi_code_matches={asfi_code_matches}; "
                f"bank_matches={bank_matches}"
            )
        )

        return ConsistencyResult(
            banco_id=record.banco_id,
            cuenta_id=record.cuenta_id,
            is_consistent=consistent,
            details=details,
        )