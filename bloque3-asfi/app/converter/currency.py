from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP


def convert_usd_to_bs(saldo_usd: Decimal, exchange_rate: Decimal) -> Decimal:
    return (saldo_usd * exchange_rate).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
