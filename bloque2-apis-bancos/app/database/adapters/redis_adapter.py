from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

import redis

from app.database.adapters.base import BaseDatabaseAdapter, CuentaId


class RedisAdapter(BaseDatabaseAdapter):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = None
        self.key_prefix = config.get("redis_key_prefix", "cuenta:")

    def connect(self) -> bool:
        try:
            self.client = redis.Redis(
                host=self.config.get("redis_host", self.config.get("host", "localhost")),
                port=self.config.get("redis_port", self.config.get("port", 6379)),
                password=self.config.get("redis_password", self.config.get("password")),
                db=self.config.get("redis_db", 0),
                decode_responses=True,
            )
            self.client.ping()
            return True
        except Exception:
            self.client = None
            return False

    def disconnect(self) -> bool:
        try:
            if self.client is not None:
                self.client.close()
            return True
        except Exception:
            return False

    def test_connection(self) -> bool:
        try:
            if self.client is None:
                return self.connect()
            self.client.ping()
            return True
        except Exception:
            return False

    def _ensure_connection(self) -> None:
        if self.client is None:
            if not self.connect():
                raise ConnectionError("No se pudo conectar a Redis")

    def _all_account_keys(self) -> List[str]:
        self._ensure_connection()
        keys = list(self.client.scan_iter(match=f"{self.key_prefix}*"))
        keys.sort()
        return keys

    def count_cuentas(self) -> int:
        return len(self._all_account_keys())

    def _build_key(self, cuenta_id: CuentaId) -> str:
        cuenta_id_str = str(cuenta_id)
        if cuenta_id_str.startswith(self.key_prefix):
            return cuenta_id_str
        return f"{self.key_prefix}{cuenta_id_str}"

    def _normalize_hash(self, row: Dict[str, Any]) -> Dict[str, Any]:
        # Redis no maneja id numérico real en este bloque; usamos nro_cuenta como id lógico.
        if "id" not in row or row.get("id") in (None, ""):
            row["id"] = row.get("nro_cuenta")
        return self.normalize_cuenta(row)

    def get_cuentas(self, limit: int, offset: int) -> List[Dict[str, Any]]:
        keys = self._all_account_keys()
        paged_keys = keys[offset: offset + limit]

        cuentas: List[Dict[str, Any]] = []
        for key in paged_keys:
            row = self.client.hgetall(key)
            if row:
                cuentas.append(self._normalize_hash(row))

        return cuentas

    def get_cuenta_by_id(self, cuenta_id: CuentaId) -> Optional[Dict[str, Any]]:
        self._ensure_connection()

        # 1) Buscar por clave Redis directa o derivada desde nro_cuenta
        key = self._build_key(cuenta_id)
        row = self.client.hgetall(key)
        if row:
            return self._normalize_hash(row)

        # 2) Fallback: buscar por campo interno nro_cuenta dentro de todos los hashes
        cuenta_id_str = str(cuenta_id)
        for redis_key in self._all_account_keys():
            candidate = self.client.hgetall(redis_key)
            if candidate and candidate.get("nro_cuenta") == cuenta_id_str:
                return self._normalize_hash(candidate)

        return None

    def actualizar_saldo(
        self,
        cuenta_id: CuentaId,
        saldo_bs: float,
        code_verif: str,
        updated_at: Optional[datetime] = None,
    ) -> bool:
        self._ensure_connection()

        key = self._build_key(cuenta_id)

        if not self.client.exists(key):
            # Fallback por nro_cuenta
            cuenta = self.get_cuenta_by_id(cuenta_id)
            if cuenta is None:
                return False
            key = self._build_key(cuenta["nro_cuenta"])

        result = self.client.hset(
            key,
            mapping={
                self.config["field_saldo_bs"]: saldo_bs,
                self.config["field_code_verif"]: code_verif,
            },
        )

        return result >= 0