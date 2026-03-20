from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Union


CuentaId = Union[int, str]


class BaseDatabaseAdapter(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None
        self.cursor = None

    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        pass

    @abstractmethod
    def count_cuentas(self) -> int:
        pass

    @abstractmethod
    def get_cuentas(self, limit: int, offset: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_cuenta_by_id(self, cuenta_id: CuentaId) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def actualizar_saldo(
        self,
        cuenta_id: CuentaId,
        saldo_bs: float,
        code_verif: str,
        updated_at: Optional[datetime] = None,
    ) -> bool:
        pass

    def normalize_bool(self, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "t", "yes", "y", "si", "sí"}
        return False

    def normalize_cuenta(self, cuenta: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normaliza cualquier registro del motor al formato interno único del bloque 2.
        Este formato debe reflejar el esquema real del bloque 1.
        """
        return {
            "id": cuenta.get("id", cuenta.get("_id")),
            "ci": cuenta.get("ci", ""),
            "nombres": cuenta.get("nombres", ""),
            "apellidos": cuenta.get("apellidos", ""),
            "nro_cuenta": cuenta.get("nro_cuenta", ""),
            "id_banco": cuenta.get("id_banco"),
            "saldo": cuenta.get("saldo"),
            "saldo_bs": cuenta.get("saldo_bs"),
            "ci_cifrado": self.normalize_bool(cuenta.get("ci_cifrado")),
            "saldo_cifrado": self.normalize_bool(cuenta.get("saldo_cifrado")),
            "code_verif": cuenta.get("code_verif"),
            "created_at": cuenta.get("created_at"),
            "created_user": cuenta.get("created_user"),
        }