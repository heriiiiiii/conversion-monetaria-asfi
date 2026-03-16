from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Iterable

from app.config import settings
from app.constants import BANK_CATALOG
from app.core.schemas import CallbackResult, ConsistencyResult, ConversionRecord, ProcessingError, RateQuote


class AsfiRepository:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or settings.sqlite_abspath
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_schema()

    def create_schema(self) -> None:
        self.conn.executescript(
            """
            PRAGMA foreign_keys = ON;
            CREATE TABLE IF NOT EXISTS Bancos (
                BancoId INTEGER PRIMARY KEY,
                Nombre TEXT NOT NULL,
                AlgoritmoEncriptacion TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS BancoLlaves (
                BancoId INTEGER PRIMARY KEY,
                Algoritmo TEXT NOT NULL,
                LlaveReferencia TEXT NOT NULL,
                TipoLlave TEXT NOT NULL,
                UltimaSincronizacion TEXT NOT NULL,
                FOREIGN KEY (BancoId) REFERENCES Bancos(BancoId)
            );
            CREATE TABLE IF NOT EXISTS Cuentas (
                CuentaId INTEGER PRIMARY KEY,
                BancoId INTEGER NOT NULL,
                SaldoUSD TEXT NOT NULL,
                SaldoBs TEXT,
                FechaConversion TEXT,
                CodigoVerificacion TEXT,
                FOREIGN KEY (BancoId) REFERENCES Bancos(BancoId)
            );
            CREATE TABLE IF NOT EXISTS AuditLog (
                AuditId INTEGER PRIMARY KEY AUTOINCREMENT,
                Timestamp TEXT NOT NULL,
                BancoId INTEGER NOT NULL,
                CuentaId INTEGER,
                Evento TEXT NOT NULL,
                Detalle TEXT,
                TipoCambio TEXT,
                ModoTipoCambio TEXT,
                LoteId TEXT
            );
            CREATE TABLE IF NOT EXISTS TipoCambioLog (
                RateLogId INTEGER PRIMARY KEY AUTOINCREMENT,
                Timestamp TEXT NOT NULL,
                Modo TEXT NOT NULL,
                TipoCambio TEXT NOT NULL,
                BaseRate TEXT NOT NULL,
                Drift TEXT NOT NULL,
                Slot INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS ProcesamientoErrores (
                ErrorId INTEGER PRIMARY KEY AUTOINCREMENT,
                Timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                BancoId INTEGER NOT NULL,
                CuentaId INTEGER,
                Etapa TEXT NOT NULL,
                Error TEXT NOT NULL,
                LoteId TEXT
            );
            CREATE TABLE IF NOT EXISTS BancoCallbacks (
                CallbackId INTEGER PRIMARY KEY AUTOINCREMENT,
                Timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                BancoId INTEGER NOT NULL,
                CuentaId INTEGER NOT NULL,
                SaldoBs TEXT NOT NULL,
                CodigoVerificacion TEXT NOT NULL,
                Accepted INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS ConsistencyChecks (
                CheckId INTEGER PRIMARY KEY AUTOINCREMENT,
                Timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                BancoId INTEGER NOT NULL,
                CuentaId INTEGER NOT NULL,
                IsConsistent INTEGER NOT NULL,
                Details TEXT NOT NULL
            );
            """
        )
        self.conn.commit()

    def truncate_all(self) -> None:
        self.conn.executescript(
            """
            DELETE FROM ConsistencyChecks;
            DELETE FROM BancoCallbacks;
            DELETE FROM ProcesamientoErrores;
            DELETE FROM TipoCambioLog;
            DELETE FROM AuditLog;
            DELETE FROM Cuentas;
            DELETE FROM BancoLlaves;
            DELETE FROM Bancos;
            """
        )
        self.conn.commit()

    def seed_banks(self, bank_mapping: list[dict[str, Any]]) -> None:
        self.conn.executemany(
            "INSERT OR REPLACE INTO Bancos (BancoId, Nombre, AlgoritmoEncriptacion) VALUES (?, ?, ?)",
            [(b["bank_id"], b["name"], b["algorithm"]) for b in BANK_CATALOG],
        )
        self.conn.executemany(
            """
            INSERT OR REPLACE INTO BancoLlaves
            (BancoId, Algoritmo, LlaveReferencia, TipoLlave, UltimaSincronizacion)
            VALUES (?, ?, ?, ?, datetime('now'))
            """,
            [(m["bank_id"], m["algorithm"], m["seed"], m["key_type"]) for m in bank_mapping],
        )
        self.conn.commit()

    def save_conversion(self, record: ConversionRecord) -> None:
        self.conn.execute(
            """
            INSERT OR REPLACE INTO Cuentas
            (CuentaId, BancoId, SaldoUSD, SaldoBs, FechaConversion, CodigoVerificacion)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                record.cuenta_id,
                record.banco_id,
                str(record.saldo_usd),
                str(record.saldo_bs),
                record.fecha_conversion,
                record.codigo_verificacion,
            ),
        )
        self.conn.commit()

    def log_audit(self, timestamp: str, banco_id: int, cuenta_id: int | None, evento: str, detalle: str, tipo_cambio: str | None = None, modo_tipo_cambio: str | None = None, lote_id: str | None = None) -> None:
        self.conn.execute(
            """
            INSERT INTO AuditLog
            (Timestamp, BancoId, CuentaId, Evento, Detalle, TipoCambio, ModoTipoCambio, LoteId)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (timestamp, banco_id, cuenta_id, evento, detalle, tipo_cambio, modo_tipo_cambio, lote_id),
        )
        self.conn.commit()

    def log_rate(self, quote: RateQuote) -> None:
        self.conn.execute(
            """
            INSERT INTO TipoCambioLog (Timestamp, Modo, TipoCambio, BaseRate, Drift, Slot)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (quote.generated_at, quote.mode, str(quote.rate), str(quote.base_rate), str(quote.drift), quote.slot),
        )
        self.conn.commit()

    def log_error(self, error: ProcessingError) -> None:
        self.conn.execute(
            """
            INSERT INTO ProcesamientoErrores (BancoId, CuentaId, Etapa, Error, LoteId)
            VALUES (?, ?, ?, ?, ?)
            """,
            (error.banco_id, error.cuenta_id, error.stage, error.error, error.lote_id),
        )
        self.conn.commit()

    def save_callback(self, callback: CallbackResult) -> None:
        self.conn.execute(
            """
            INSERT INTO BancoCallbacks (BancoId, CuentaId, SaldoBs, CodigoVerificacion, Accepted)
            VALUES (?, ?, ?, ?, ?)
            """,
            (callback.banco_id, callback.cuenta_id, str(callback.saldo_bs), callback.codigo_verificacion, 1 if callback.accepted else 0),
        )
        self.conn.commit()

    def save_consistency(self, result: ConsistencyResult) -> None:
        self.conn.execute(
            """
            INSERT INTO ConsistencyChecks (BancoId, CuentaId, IsConsistent, Details)
            VALUES (?, ?, ?, ?)
            """,
            (result.banco_id, result.cuenta_id, 1 if result.is_consistent else 0, result.details),
        )
        self.conn.commit()

    def fetch_recent_audit(self, limit: int = 20) -> list[dict[str, Any]]:
        cur = self.conn.execute(
            "SELECT * FROM AuditLog ORDER BY AuditId DESC LIMIT ?",
            (limit,),
        )
        return [dict(row) for row in cur.fetchall()]

    def fetch_account(self, cuenta_id: int) -> dict[str, Any] | None:
        cur = self.conn.execute("SELECT * FROM Cuentas WHERE CuentaId = ?", (cuenta_id,))
        row = cur.fetchone()
        return dict(row) if row else None
