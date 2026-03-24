from __future__ import annotations

from typing import Any, Dict

from app.core.config import settings
from app.database.adapters.base import BaseDatabaseAdapter
from app.database.adapters.mongodb_adapter import MongoDBAdapter
from app.database.adapters.mysql_adapter import MySQLAdapter
from app.database.adapters.postgresql_adapter import PostgreSQLAdapter
from app.database.adapters.redis_adapter import RedisAdapter

try:
    from app.database.adapters.mariadb_adapter import MariaDBAdapter
except ImportError:
    MariaDBAdapter = None


class DatabaseConnector:
    def __init__(self) -> None:
        self.db_type = settings.DB_ENGINE.strip().lower()
        self.adapter: BaseDatabaseAdapter = self._initialize_adapter()

    def _build_config(self) -> Dict[str, Any]:
        return {
            "engine": settings.DB_ENGINE,
            "host": settings.DB_HOST,
            "port": settings.DB_PORT,
            "user": settings.DB_USER,
            "password": settings.DB_PASSWORD,
            "database": settings.DB_NAME,
            "table": settings.DB_TABLE,
            "mongodb_uri": settings.MONGODB_URI,
            "mongodb_database": settings.MONGODB_DATABASE,
            "mongodb_collection": settings.MONGODB_COLLECTION,
            "redis_host": settings.REDIS_HOST,
            "redis_port": settings.REDIS_PORT,
            "redis_password": settings.REDIS_PASSWORD,
            "redis_db": settings.REDIS_DB,
            "redis_key_prefix": settings.REDIS_KEY_PREFIX,
            "field_id": settings.FIELD_ID,
            "field_ci": settings.FIELD_CI,
            "field_nombres": settings.FIELD_NOMBRES,
            "field_apellidos": settings.FIELD_APELLIDOS,
            "field_nro_cuenta": settings.FIELD_NRO_CUENTA,
            "field_banco_id": settings.FIELD_BANCO_ID,
            "field_saldo_usd": settings.FIELD_SALDO_USD,
            "field_saldo_bs": settings.FIELD_SALDO_BS,
            "field_ci_cifrado": settings.FIELD_CI_CIFRADO,
            "field_saldo_cifrado": settings.FIELD_SALDO_CIFRADO,
            "field_code_verif": settings.FIELD_CODE_VERIF,
        }

    def _initialize_adapter(self) -> BaseDatabaseAdapter:
        config = self._build_config()

        if self.db_type == "mysql":
            adapter: BaseDatabaseAdapter = MySQLAdapter(config)
        elif self.db_type == "mariadb":
            if MariaDBAdapter is None:
                raise ValueError("MariaDBAdapter no está disponible")
            adapter = MariaDBAdapter(config)
        elif self.db_type in {"postgresql", "postgres", "psql"}:
            adapter = PostgreSQLAdapter(config)
        elif self.db_type == "mongodb":
            adapter = MongoDBAdapter(config)
        elif self.db_type == "redis":
            adapter = RedisAdapter(config)
        else:
            raise ValueError(f"Motor no soportado: {self.db_type}")

        if not adapter.connect():
            raise ConnectionError(f"No se pudo conectar al motor {self.db_type}")

        return adapter

    def test_connection(self) -> bool:
        return self.adapter.test_connection()

    def count_cuentas(self) -> int:
        return self.adapter.count_cuentas()

    def get_cuentas(self, limit: int, offset: int):
        return self.adapter.get_cuentas(limit=limit, offset=offset)

    def get_cuenta_by_id(self, cuenta_id):
        return self.adapter.get_cuenta_by_id(cuenta_id)

    def actualizar_saldo(self, cuenta_id, saldo_bs: float, code_verif: str) -> bool:
        return self.adapter.actualizar_saldo(
            cuenta_id=cuenta_id,
            saldo_bs=saldo_bs,
            code_verif=code_verif,
        )


db_connector = DatabaseConnector()