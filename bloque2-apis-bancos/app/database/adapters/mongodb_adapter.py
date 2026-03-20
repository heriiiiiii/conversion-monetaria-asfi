from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.database.adapters.base import BaseDatabaseAdapter, CuentaId


class MongoDBAdapter(BaseDatabaseAdapter):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = None
        self.database = None
        self.collection = None

    def connect(self) -> bool:
        try:
            uri = self.config.get("mongodb_uri")
            host = self.config.get("host", "localhost")
            port = self.config.get("port", 27017)
            database_name = self.config.get("mongodb_database") or self.config.get("database")
            collection_name = self.config.get("mongodb_collection", "cuentas")

            if uri:
                self.client = MongoClient(uri)
            else:
                self.client = MongoClient(host=host, port=port)

            self.database = self.client[database_name]
            self.collection = self.database[collection_name]
            self.client.admin.command("ping")
            return True
        except Exception:
            self.client = None
            self.database = None
            self.collection = None
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
            self.client.admin.command("ping")
            return True
        except Exception:
            return False

    def _ensure_connection(self) -> None:
        if self.client is None or self.collection is None:
            if not self.connect():
                raise ConnectionError("No se pudo conectar a MongoDB")

    def count_cuentas(self) -> int:
        self._ensure_connection()
        return int(self.collection.count_documents({}))

    def get_cuentas(self, limit: int, offset: int) -> List[Dict[str, Any]]:
        self._ensure_connection()

        cursor = (
            self.collection.find({})
            .sort("_id", 1)
            .skip(offset)
            .limit(limit)
        )

        rows = list(cursor)
        normalized: List[Dict[str, Any]] = []

        for row in rows:
            if "_id" in row:
                row["_id"] = str(row["_id"])
            normalized.append(self.normalize_cuenta(row))

        return normalized

    def get_cuenta_by_id(self, cuenta_id: CuentaId) -> Optional[Dict[str, Any]]:
        self._ensure_connection()

        # En el bloque 1 Mongo usa _id como identificador principal
        row = self.collection.find_one({"_id": cuenta_id})

        # Fallback útil si luego quieren buscar por nro_cuenta
        if row is None:
            row = self.collection.find_one({"nro_cuenta": str(cuenta_id)})

        if row is None:
            return None

        row["_id"] = str(row["_id"])
        return self.normalize_cuenta(row)

    def actualizar_saldo(
        self,
        cuenta_id: CuentaId,
        saldo_bs: float,
        code_verif: str,
        updated_at: Optional[datetime] = None,
    ) -> bool:
        self._ensure_connection()

        try:
            result = self.collection.update_one(
                {"_id": cuenta_id},
                {
                    "$set": {
                        self.config["field_saldo_bs"]: saldo_bs,
                        self.config["field_code_verif"]: code_verif,
                    }
                },
            )

            if result.matched_count == 0:
                result = self.collection.update_one(
                    {"nro_cuenta": str(cuenta_id)},
                    {
                        "$set": {
                            self.config["field_saldo_bs"]: saldo_bs,
                            self.config["field_code_verif"]: code_verif,
                        }
                    },
                )

            return result.modified_count > 0 or result.matched_count > 0
        except PyMongoError:
            raise