from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict

from app.crypto.algorithms import decrypt_text
from app.crypto.key_registry import KeyRegistry


class DecryptorService:
    def __init__(self, key_registry: KeyRegistry | None = None) -> None:
        self.key_registry = key_registry or KeyRegistry()

    def decrypt_fields(
        self,
        bank_id: int,
        algorithm: str,
        account_payload: Dict[str, Any],
        encrypted_fields: set[str],
    ) -> Dict[str, Any]:
        material = self.key_registry.get(bank_id)
        result = dict(account_payload)

        for field in encrypted_fields:
            if field not in account_payload:
                raise KeyError(f"El campo cifrado '{field}' no existe en el payload recibido.")

            encrypted_value = account_payload[field]
            decrypted_value = decrypt_text(algorithm, encrypted_value, material)

            if field == "saldo_usd":
                result[field] = Decimal(str(decrypted_value))
            else:
                result[field] = decrypted_value

        if "saldo_usd" in result and not isinstance(result["saldo_usd"], Decimal):
            result["saldo_usd"] = Decimal(str(result["saldo_usd"]))

        return result