from __future__ import annotations

import sqlite3
import threading
from pathlib import Path
from typing import Any, Sequence

from app.config import settings
from app.core.schemas import AuditEvent, CallbackResult, ConsistencyResult, ConversionRecord, ProcessingError, RateQuote


class AsfiRepository:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or settings.sqlite_abspath
        self._lock = threading.RLock()
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._apply_pragmas()
        self.create_schema()

    def _apply_pragmas(self) -> None:
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.execute("PRAGMA journal_mode = WAL;")
        self.conn.execute("PRAGMA synchronous = NORMAL;")
        self.conn.execute("PRAGMA temp_store = MEMORY;")

    def create_schema(self) -> None:
        with self._lock:
            self.conn.executescript(
                """
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
                    FuenteTipoCambio TEXT,
                    LoteId TEXT
                );
                CREATE TABLE IF NOT EXISTS TipoCambioLog (
                    RateLogId INTEGER PRIMARY KEY AUTOINCREMENT,
                    Timestamp TEXT NOT NULL,
                    Modo TEXT NOT NULL,
                    TipoCambio TEXT NOT NULL,
                    BaseRate TEXT NOT NULL,
                    Drift TEXT NOT NULL,
                    Slot INTEGER NOT NULL,
                    Source TEXT NOT NULL
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
                    Accepted INTEGER NOT NULL,
                    UpdatedAt TEXT NOT NULL
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
            self._run_migrations()
            self.conn.commit()


    def _run_migrations(self) -> None:
        self._ensure_column("AuditLog", "FuenteTipoCambio", "TEXT")
        self._ensure_column("TipoCambioLog", "Source", "TEXT DEFAULT 'ASFI_BCB_INTERNAL'")
        self._ensure_column("BancoCallbacks", "UpdatedAt", "TEXT")

    def _ensure_column(self, table_name: str, column_name: str, ddl: str) -> None:
        cur = self.conn.execute(f"PRAGMA table_info({table_name})")
        existing = {row[1] for row in cur.fetchall()}
        if column_name not in existing:
            self.conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {ddl}")

    def truncate_all(self) -> None:
        with self._lock:
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
        bancos_rows = [(b["bank_id"], b["name"], b["algorithm"]) for b in bank_mapping]
        key_rows = [(m["bank_id"], m["algorithm"], m["seed"], m["key_type"]) for m in bank_mapping]
        with self._lock:
            self.conn.executemany(
                "INSERT OR REPLACE INTO Bancos (BancoId, Nombre, AlgoritmoEncriptacion) VALUES (?, ?, ?)",
                bancos_rows,
            )
            self.conn.executemany(
                """
                INSERT OR REPLACE INTO BancoLlaves
                (BancoId, Algoritmo, LlaveReferencia, TipoLlave, UltimaSincronizacion)
                VALUES (?, ?, ?, ?, datetime('now'))
                """,
                key_rows,
            )
            self.conn.commit()

    def save_conversion(self, record: ConversionRecord) -> None:
        self.save_conversions_batch([record])

    def save_conversions_batch(self, records: Sequence[ConversionRecord]) -> None:
        if not records:
            return
        rows = [
            (
                record.cuenta_id,
                record.banco_id,
                str(record.saldo_usd),
                str(record.saldo_bs),
                record.fecha_conversion,
                record.codigo_verificacion,
            )
            for record in records
        ]
        with self._lock:
            self.conn.executemany(
                """
                INSERT OR REPLACE INTO Cuentas
                (CuentaId, BancoId, SaldoUSD, SaldoBs, FechaConversion, CodigoVerificacion)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
            self.conn.commit()

    def log_audit(self, timestamp: str, banco_id: int, cuenta_id: int | None, evento: str, detalle: str, tipo_cambio: str | None = None, modo_tipo_cambio: str | None = None, fuente_tipo_cambio: str | None = None, lote_id: str | None = None) -> None:
        self.log_audit_batch(
            [
                AuditEvent(
                    timestamp=timestamp,
                    banco_id=banco_id,
                    cuenta_id=cuenta_id,
                    evento=evento,
                    detalle=detalle,
                    tipo_cambio=tipo_cambio,
                    modo_tipo_cambio=modo_tipo_cambio,
                    fuente_tipo_cambio=fuente_tipo_cambio,
                    lote_id=lote_id,
                )
            ]
        )

    def log_audit_batch(self, events: Sequence[AuditEvent]) -> None:
        if not events:
            return
        rows = [
            (
                item.timestamp,
                item.banco_id,
                item.cuenta_id,
                item.evento,
                item.detalle,
                item.tipo_cambio,
                item.modo_tipo_cambio,
                item.fuente_tipo_cambio,
                item.lote_id,
            )
            for item in events
        ]
        with self._lock:
            self.conn.executemany(
                """
                INSERT INTO AuditLog
                (Timestamp, BancoId, CuentaId, Evento, Detalle, TipoCambio, ModoTipoCambio, FuenteTipoCambio, LoteId)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
            self.conn.commit()

    def log_rate(self, quote: RateQuote) -> None:
        with self._lock:
            self.conn.execute(
                """
                INSERT INTO TipoCambioLog (Timestamp, Modo, TipoCambio, BaseRate, Drift, Slot, Source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (quote.generated_at, quote.mode, str(quote.rate), str(quote.base_rate), str(quote.drift), quote.slot, quote.source),
            )
            self.conn.commit()

    def log_error(self, error: ProcessingError) -> None:
        self.log_errors_batch([error])

    def log_errors_batch(self, errors: Sequence[ProcessingError]) -> None:
        if not errors:
            return
        rows = [(error.banco_id, error.cuenta_id, error.stage, error.error, error.lote_id) for error in errors]
        with self._lock:
            self.conn.executemany(
                """
                INSERT INTO ProcesamientoErrores (BancoId, CuentaId, Etapa, Error, LoteId)
                VALUES (?, ?, ?, ?, ?)
                """,
                rows,
            )
            self.conn.commit()

    def save_callback(self, callback: CallbackResult) -> None:
        self.save_callbacks_batch([callback])

    def save_callbacks_batch(self, callbacks: Sequence[CallbackResult]) -> None:
        if not callbacks:
            return
        rows = [
            (
                callback.banco_id,
                callback.cuenta_id,
                str(callback.saldo_bs),
                callback.codigo_verificacion,
                1 if callback.accepted else 0,
                callback.updated_at,
            )
            for callback in callbacks
        ]
        with self._lock:
            self.conn.executemany(
                """
                INSERT INTO BancoCallbacks (BancoId, CuentaId, SaldoBs, CodigoVerificacion, Accepted, UpdatedAt)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
            self.conn.commit()

    def save_consistency(self, result: ConsistencyResult) -> None:
        self.save_consistency_batch([result])

    def save_consistency_batch(self, results: Sequence[ConsistencyResult]) -> None:
        if not results:
            return
        rows = [(result.banco_id, result.cuenta_id, 1 if result.is_consistent else 0, result.details) for result in results]
        with self._lock:
            self.conn.executemany(
                """
                INSERT INTO ConsistencyChecks (BancoId, CuentaId, IsConsistent, Details)
                VALUES (?, ?, ?, ?)
                """,
                rows,
            )
            self.conn.commit()

    def fetch_recent_audit(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._lock:
            cur = self.conn.execute(
                "SELECT * FROM AuditLog ORDER BY AuditId DESC LIMIT ?",
                (limit,),
            )
            return [dict(row) for row in cur.fetchall()]

    def fetch_account(self, cuenta_id: int) -> dict[str, Any] | None:
        with self._lock:
            cur = self.conn.execute("SELECT * FROM Cuentas WHERE CuentaId = ?", (cuenta_id,))
            row = cur.fetchone()
            return dict(row) if row else None
