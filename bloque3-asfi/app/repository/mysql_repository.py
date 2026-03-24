from __future__ import annotations

import threading
import time
from datetime import datetime, timezone
from typing import Any, Sequence

import mysql.connector

from app.config import settings
from app.core.schemas import (
    AuditEvent,
    CallbackResult,
    ConsistencyResult,
    ConversionRecord,
    ProcessingError,
    RateQuote,
)


def _to_mysql_datetime(value: str | datetime | None) -> str | None:
    if value is None:
        return None

    if isinstance(value, datetime):
        dt = value
    else:
        raw = value.strip()
        try:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return raw.replace("T", " ")

    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)

    return dt.strftime("%Y-%m-%d %H:%M:%S.%f")


class AsfiRepository:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self.conn = None
        self._connect()
        self.create_schema()

    def _connect(self) -> None:
        last_error = None

        for attempt in range(settings.mysql_connect_retries):
            try:
                self.conn = mysql.connector.connect(
                    host=settings.mysql_host,
                    port=settings.mysql_port,
                    user=settings.mysql_user,
                    password=settings.mysql_password,
                    database=settings.mysql_database,
                    autocommit=False,
                    connection_timeout=settings.mysql_connection_timeout,
                )
                return
            except mysql.connector.Error as exc:
                last_error = exc
                if attempt < settings.mysql_connect_retries - 1:
                    time.sleep(settings.mysql_connect_retry_delay)

        raise last_error

    def create_schema(self) -> None:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS Bancos (
                    BancoId INT PRIMARY KEY,
                    Nombre VARCHAR(100) NOT NULL,
                    AlgoritmoEncriptacion VARCHAR(50) NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS BancoLlaves (
                    BancoId INT PRIMARY KEY,
                    Algoritmo VARCHAR(50) NOT NULL,
                    LlaveReferencia VARCHAR(255) NOT NULL,
                    TipoLlave VARCHAR(20) NOT NULL,
                    UltimaSincronizacion DATETIME NOT NULL,
                    FOREIGN KEY (BancoId) REFERENCES Bancos(BancoId)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS Cuentas (
                    CuentaId VARCHAR(255) NOT NULL,
                    BancoId INT NOT NULL,
                    SaldoUSD DECIMAL(18,4) NOT NULL,
                    SaldoBs DECIMAL(18,4) NULL,
                    FechaConversion DATETIME NULL,
                    CodigoVerificacion CHAR(8) NULL,
                    PRIMARY KEY (CuentaId, BancoId),
                    CONSTRAINT fk_cuentas_bancos
                        FOREIGN KEY (BancoId) REFERENCES Bancos(BancoId)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS AuditLog (
                    AuditId BIGINT AUTO_INCREMENT PRIMARY KEY,
                    Timestamp DATETIME NOT NULL,
                    BancoId INT NOT NULL,
                    CuentaId VARCHAR(255) NULL,
                    Evento VARCHAR(50) NOT NULL,
                    Detalle TEXT NULL,
                    TipoCambio DECIMAL(18,4) NULL,
                    ModoTipoCambio VARCHAR(20) NULL,
                    FuenteTipoCambio VARCHAR(50) NULL,
                    LoteId VARCHAR(100) NULL,
                    INDEX idx_audit_banco_cuenta (BancoId, CuentaId),
                    INDEX idx_audit_timestamp (Timestamp),
                    FOREIGN KEY (BancoId) REFERENCES Bancos(BancoId)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS TipoCambioLog (
                    RateLogId BIGINT AUTO_INCREMENT PRIMARY KEY,
                    Timestamp DATETIME NOT NULL,
                    Modo VARCHAR(20) NOT NULL,
                    TipoCambio DECIMAL(18,4) NOT NULL,
                    BaseRate DECIMAL(18,4) NOT NULL,
                    Drift DECIMAL(18,4) NOT NULL,
                    Slot BIGINT NOT NULL,
                    Source VARCHAR(50) NOT NULL,
                    INDEX idx_rate_mode_time (Modo, Timestamp)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS ProcesamientoErrores (
                    ErrorId BIGINT AUTO_INCREMENT PRIMARY KEY,
                    Timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    BancoId INT NOT NULL,
                    CuentaId VARCHAR(255) NULL,
                    Etapa VARCHAR(50) NOT NULL,
                    Error TEXT NOT NULL,
                    LoteId VARCHAR(100) NULL,
                    INDEX idx_error_banco_cuenta (BancoId, CuentaId),
                    FOREIGN KEY (BancoId) REFERENCES Bancos(BancoId)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS BancoCallbacks (
                    CallbackId BIGINT AUTO_INCREMENT PRIMARY KEY,
                    Timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    BancoId INT NOT NULL,
                    CuentaId VARCHAR(255) NOT NULL,
                    SaldoBs DECIMAL(18,4) NOT NULL,
                    CodigoVerificacion CHAR(8) NOT NULL,
                    Accepted BOOLEAN NOT NULL,
                    UpdatedAt DATETIME NOT NULL,
                    INDEX idx_callback_banco_cuenta (BancoId, CuentaId),
                    FOREIGN KEY (BancoId) REFERENCES Bancos(BancoId)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS ConsistencyChecks (
                    CheckId BIGINT AUTO_INCREMENT PRIMARY KEY,
                    Timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    BancoId INT NOT NULL,
                    CuentaId VARCHAR(255) NOT NULL,
                    IsConsistent BOOLEAN NOT NULL,
                    Details TEXT NOT NULL,
                    INDEX idx_consistency_banco_cuenta (BancoId, CuentaId),
                    FOREIGN KEY (BancoId) REFERENCES Bancos(BancoId)
                )
                """
            )
            cursor.close()
            self.conn.commit()

    def truncate_all(self) -> None:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM ConsistencyChecks")
            cursor.execute("DELETE FROM BancoCallbacks")
            cursor.execute("DELETE FROM ProcesamientoErrores")
            cursor.execute("DELETE FROM TipoCambioLog")
            cursor.execute("DELETE FROM AuditLog")
            cursor.execute("DELETE FROM Cuentas")
            cursor.execute("DELETE FROM BancoLlaves")
            cursor.execute("DELETE FROM Bancos")
            cursor.close()
            self.conn.commit()

    def seed_banks(self, bank_mapping: list[dict[str, Any]]) -> None:
        bancos_rows = [(b["bank_id"], b["name"], b["algorithm"]) for b in bank_mapping]
        key_rows = [
            (
                m["bank_id"],
                m["algorithm"],
                m["seed"],
                m["key_type"],
                datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            )
            for m in bank_mapping
        ]
        with self._lock:
            cursor = self.conn.cursor()
            cursor.executemany(
                """
                INSERT INTO Bancos (BancoId, Nombre, AlgoritmoEncriptacion)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    Nombre = VALUES(Nombre),
                    AlgoritmoEncriptacion = VALUES(AlgoritmoEncriptacion)
                """,
                bancos_rows,
            )
            cursor.executemany(
                """
                INSERT INTO BancoLlaves
                (BancoId, Algoritmo, LlaveReferencia, TipoLlave, UltimaSincronizacion)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    Algoritmo = VALUES(Algoritmo),
                    LlaveReferencia = VALUES(LlaveReferencia),
                    TipoLlave = VALUES(TipoLlave),
                    UltimaSincronizacion = VALUES(UltimaSincronizacion)
                """,
                key_rows,
            )
            cursor.close()
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
                _to_mysql_datetime(record.fecha_conversion),
                record.codigo_verificacion,
            )
            for record in records
        ]

        with self._lock:
            cursor = self.conn.cursor()
            cursor.executemany(
                """
                INSERT INTO Cuentas
                (CuentaId, BancoId, SaldoUSD, SaldoBs, FechaConversion, CodigoVerificacion)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    SaldoUSD = VALUES(SaldoUSD),
                    SaldoBs = VALUES(SaldoBs),
                    FechaConversion = VALUES(FechaConversion),
                    CodigoVerificacion = VALUES(CodigoVerificacion)
                """,
                rows,
            )
            cursor.close()
            self.conn.commit()

    def log_audit(
        self,
        timestamp: str,
        banco_id: int,
        cuenta_id: str | None,
        evento: str,
        detalle: str,
        tipo_cambio: str | None = None,
        modo_tipo_cambio: str | None = None,
        fuente_tipo_cambio: str | None = None,
        lote_id: str | None = None,
    ) -> None:
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
                _to_mysql_datetime(item.timestamp),
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
            cursor = self.conn.cursor()
            cursor.executemany(
                """
                INSERT INTO AuditLog
                (Timestamp, BancoId, CuentaId, Evento, Detalle, TipoCambio, ModoTipoCambio, FuenteTipoCambio, LoteId)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                rows,
            )
            cursor.close()
            self.conn.commit()

    def log_rate(self, quote: RateQuote) -> None:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO TipoCambioLog (Timestamp, Modo, TipoCambio, BaseRate, Drift, Slot, Source)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    _to_mysql_datetime(quote.generated_at),
                    quote.mode,
                    str(quote.rate),
                    str(quote.base_rate),
                    str(quote.drift),
                    quote.slot,
                    quote.source,
                ),
            )
            cursor.close()
            self.conn.commit()

    def log_error(self, error: ProcessingError) -> None:
        self.log_errors_batch([error])

    def log_errors_batch(self, errors: Sequence[ProcessingError]) -> None:
        if not errors:
            return

        rows = [
            (
                error.banco_id,
                error.cuenta_id,
                error.stage,
                error.error,
                error.lote_id,
            )
            for error in errors
        ]

        with self._lock:
            cursor = self.conn.cursor()
            cursor.executemany(
                """
                INSERT INTO ProcesamientoErrores (BancoId, CuentaId, Etapa, Error, LoteId)
                VALUES (%s, %s, %s, %s, %s)
                """,
                rows,
            )
            cursor.close()
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
                _to_mysql_datetime(callback.updated_at),
            )
            for callback in callbacks
        ]

        with self._lock:
            cursor = self.conn.cursor()
            cursor.executemany(
                """
                INSERT INTO BancoCallbacks (BancoId, CuentaId, SaldoBs, CodigoVerificacion, Accepted, UpdatedAt)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                rows,
            )
            cursor.close()
            self.conn.commit()

    def save_consistency(self, result: ConsistencyResult) -> None:
        self.save_consistency_batch([result])

    def save_consistency_batch(self, results: Sequence[ConsistencyResult]) -> None:
        if not results:
            return

        rows = [
            (
                result.banco_id,
                result.cuenta_id,
                1 if result.is_consistent else 0,
                result.details,
            )
            for result in results
        ]

        with self._lock:
            cursor = self.conn.cursor()
            cursor.executemany(
                """
                INSERT INTO ConsistencyChecks (BancoId, CuentaId, IsConsistent, Details)
                VALUES (%s, %s, %s, %s)
                """,
                rows,
            )
            cursor.close()
            self.conn.commit()

    def fetch_recent_audit(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._lock:
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM AuditLog ORDER BY AuditId DESC LIMIT %s",
                (limit,),
            )
            rows = cursor.fetchall()
            cursor.close()
            return [dict(row) for row in rows]

    def fetch_account(self, cuenta_id: str, banco_id: int) -> dict[str, Any] | None:
        with self._lock:
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM Cuentas WHERE CuentaId = %s AND BancoId = %s",
                (cuenta_id, banco_id),
            )
            row = cursor.fetchone()
            cursor.close()
            return dict(row) if row else None

    def close(self) -> None:
        with self._lock:
            if getattr(self, "conn", None) is not None:
                self.conn.close()
                self.conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()