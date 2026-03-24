from __future__ import annotations
 
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
 
from app.config import settings
from app.core.schemas import RateQuote
 
 
@dataclass(slots=True)
class DynamicRateService:
    interval_seconds: float = 0.05
    official_base: Decimal = settings.official_base
    referential_base: Decimal = settings.referential_base
    source: str = "ASFI_BCB_INTERNAL"
 
    def current_rate(self, mode: str = "OFICIAL") -> RateQuote:
        mode = mode.upper()
        if mode not in {"OFICIAL", "REFERENCIAL"}:
            raise ValueError("El modo de tipo de cambio debe ser OFICIAL o REFERENCIAL.")
 
        now = datetime.now(timezone.utc)
        slot = int(now.timestamp() / self.interval_seconds)
 
        digest = hashlib.sha256(f"{mode}:{slot}".encode("utf-8")).hexdigest()
        raw = int(digest[:8], 16) % 19999
        drift = (Decimal(raw) - Decimal("9999")) / Decimal("10000")
        drift = drift.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
 
        base_rate = self.official_base if mode == "OFICIAL" else self.referential_base
        rate = (base_rate + drift).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
 
        return RateQuote(
            mode=mode,
            rate=rate,
            generated_at=now.isoformat(),
            slot=slot,
            base_rate=base_rate,
            drift=drift,
            source=self.source,
        )