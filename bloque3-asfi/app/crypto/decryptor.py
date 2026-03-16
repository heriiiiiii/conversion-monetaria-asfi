from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict

from app.crypto.algorithms import decrypt_text
from app.crypto.key_registry import KeyRegistry


class DecryptorService:
    def __init__(self, key_registry: KeyRegistry | None = None) -> None:
        self.key_registry = key_registry or KeyRegistry()

    def decrypt_fields(self, bank_id: int, algorithm: str, account_payload: Dict[str, Any], encrypted_fields: set[str]) -> Dict[str, Any]:
        material = self.key_registry.get(bank_id)
        result = dict(account_payload)
        for field in encrypted_fields:
            envelope = account_payload[field]
            value = decrypt_text(algorithm, envelope, material)
            if field == "saldo_usd":
                result[field] = Decimal(value)
            else:
                result[field] = value
        if "saldo_usd" in result and not isinstance(result["saldo_usd"], Decimal):
            result["saldo_usd"] = Decimal(str(result["saldo_usd"]))
        return result
