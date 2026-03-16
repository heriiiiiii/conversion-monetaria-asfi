from __future__ import annotations

import secrets
from collections import OrderedDict
from datetime import datetime, timedelta, timezone


class NonceStore:
    def __init__(self, ttl_seconds: int = 300) -> None:
        self.ttl_seconds = ttl_seconds
        self._values: OrderedDict[str, datetime] = OrderedDict()

    def _purge(self) -> None:
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(seconds=self.ttl_seconds)
        expired = [key for key, value in self._values.items() if value < cutoff]
        for key in expired:
            self._values.pop(key, None)

    def seen(self, nonce: str) -> bool:
        self._purge()
        return nonce in self._values

    def register(self, nonce: str) -> None:
        self._purge()
        self._values[nonce] = datetime.now(timezone.utc)


def generate_nonce(size: int = 16) -> str:
    return secrets.token_hex(size)


def generate_verification_code() -> str:
    return secrets.token_hex(4).upper()
