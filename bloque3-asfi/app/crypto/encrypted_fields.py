from __future__ import annotations

from typing import Iterable, Set


ALLOWED_CLEAR_FIELDS = {"nombres", "apellidos", "nro_cuenta"}


class EncryptedFieldsInterpreter:
    def resolve(self, campos_cifrados: Iterable[str]) -> Set[str]:
        normalized = {field.strip().lower() for field in campos_cifrados if field and field.strip()}
        invalid = normalized.intersection(ALLOWED_CLEAR_FIELDS)
        if invalid:
            raise ValueError(
                f"Los campos {sorted(invalid)} no deben venir cifrados según el contrato del bloque 2."
            )
        return normalized
