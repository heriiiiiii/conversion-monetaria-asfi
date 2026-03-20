from __future__ import annotations

from typing import Iterable, Set


FIELD_NAME_MAP = {
    "ci": "identificacion",
    "identificacion": "identificacion",
    "saldo_usd": "saldo_usd",
    "saldousd": "saldo_usd",
    "nombres": "nombres",
    "apellidos": "apellidos",
    "nrocuenta": "nro_cuenta",
    "nro_cuenta": "nro_cuenta",
}

ALLOWED_CLEAR_FIELDS = {"nombres", "apellidos", "nro_cuenta"}


class EncryptedFieldsInterpreter:
    def resolve(self, campos_cifrados: Iterable[str]) -> Set[str]:
        normalized: Set[str] = set()

        for field in campos_cifrados:
            if not field or not str(field).strip():
                continue

            raw = str(field).strip().lower()
            internal_name = FIELD_NAME_MAP.get(raw, raw)
            normalized.add(internal_name)

        invalid = normalized.intersection(ALLOWED_CLEAR_FIELDS)
        if invalid:
            raise ValueError(
                f"Los campos {sorted(invalid)} no deben venir cifrados según el contrato del bloque 2."
            )

        return normalized