from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

import psycopg2
import psycopg2.extras

from app.database.adapters.base import BaseDatabaseAdapter, CuentaId


class PostgreSQLAdapter(BaseDatabaseAdapter):
    def connect(self) -> bool:
        try:
            self.connection = psycopg2.connect(
                host=self.config.get("host", "localhost"),
                port=self.config.get("port", 5432),
                user=self.config.get("user"),
                password=self.config.get("password"),
                dbname=self.config.get("database"),
            )
            self.cursor = self.connection.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            return True
        except Exception:
            self.connection = None
            self.cursor = None
            return False

    def disconnect(self) -> bool:
        try:
            if self.cursor is not None:
                self.cursor.close()
            if self.connection is not None:
                self.connection.close()
            return True
        except Exception:
            return False

    def test_connection(self) -> bool:
        try:
            if self.connection is None or self.connection.closed != 0:
                return self.connect()
            self.cursor.execute("SELECT 1")
            self.cursor.fetchone()
            return True
        except Exception:
            return False

    def _ensure_connection(self) -> None:
        if self.connection is None or self.connection.closed != 0:
            if not self.connect():
                raise ConnectionError("No se pudo conectar a PostgreSQL")

    def count_cuentas(self) -> int:
        self._ensure_connection()

        table = self.config["table"]
        query = f'SELECT COUNT(*) AS total FROM "{table}"'
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        return int(row["total"]) if row else 0

    def get_cuentas(self, limit: int, offset: int) -> List[Dict[str, Any]]:
        self._ensure_connection()

        table = self.config["table"]
        field_id = self.config["field_id"]

        query = f'''
            SELECT *
            FROM "{table}"
            ORDER BY "{field_id}" ASC
            LIMIT %s OFFSET %s
        '''
        self.cursor.execute(query, (limit, offset))
        rows = self.cursor.fetchall() or []
        return [self.normalize_cuenta(dict(row)) for row in rows]

    def get_cuenta_by_id(self, cuenta_id: CuentaId) -> Optional[Dict[str, Any]]:
        self._ensure_connection()

        table = self.config["table"]
        field_id = self.config["field_id"]

        query = f'''
            SELECT *
            FROM "{table}"
            WHERE "{field_id}" = %s
            LIMIT 1
        '''
        self.cursor.execute(query, (cuenta_id,))
        row = self.cursor.fetchone()
        return self.normalize_cuenta(dict(row)) if row else None

    def actualizar_saldo(
        self,
        cuenta_id: CuentaId,
        saldo_bs: float,
        code_verif: str,
        updated_at: Optional[datetime] = None,
    ) -> bool:
        self._ensure_connection()

        table = self.config["table"]
        field_id = self.config["field_id"]
        field_saldo_bs = self.config["field_saldo_bs"]
        field_code_verif = self.config["field_code_verif"]

        query = f'''
            UPDATE "{table}"
            SET "{field_saldo_bs}" = %s,
                "{field_code_verif}" = %s
            WHERE "{field_id}" = %s
        '''

        try:
            self.cursor.execute(query, (saldo_bs, code_verif, cuenta_id))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except Exception:
            self.connection.rollback()
            raise