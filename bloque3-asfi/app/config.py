from __future__ import annotations

import os
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path


@dataclass(slots=True)
class Settings:
    db_engine: str = os.getenv("ASFI_DB_ENGINE", "sqlite")
    sqlite_path: str = os.getenv("ASFI_SQLITE_PATH", "./data/asfi_central_demo.sqlite3")
    mysql_host: str = os.getenv("ASFI_MYSQL_HOST", "localhost")
    mysql_port: int = int(os.getenv("ASFI_MYSQL_PORT", "3306"))
    mysql_user: str = os.getenv("ASFI_MYSQL_USER", "root")
    mysql_password: str = os.getenv("ASFI_MYSQL_PASSWORD", "root")
    mysql_database: str = os.getenv("ASFI_MYSQL_DATABASE", "ASFI_Central")
    rate_mode: str = os.getenv("ASFI_RATE_MODE", "OFICIAL")
    rate_interval_seconds: int = int(os.getenv("ASFI_RATE_INTERVAL_SECONDS", "180"))
    official_base: Decimal = Decimal(os.getenv("ASFI_RATE_OFFICIAL_BASE", "6.9600"))
    referential_base: Decimal = Decimal(os.getenv("ASFI_RATE_REFERENTIAL_BASE", "6.8600"))
    nonce_ttl_seconds: int = int(os.getenv("ASFI_NONCE_TTL_SECONDS", "300"))
    bank_timeout_seconds: int = int(os.getenv("ASFI_BANK_TIMEOUT_SECONDS", "20"))
    processing_workers: int = int(os.getenv("ASFI_PROCESSING_WORKERS", "8"))
    encrypt_large_amount_threshold: Decimal = Decimal(os.getenv("ASFI_ENCRYPT_LARGE_AMOUNT_THRESHOLD", "100000.0000"))
    logs_dir: str = os.getenv("ASFI_LOGS_DIR", "./logs")
    project_root: Path = Path(__file__).resolve().parent.parent

    @property
    def sqlite_abspath(self) -> Path:
        path = Path(self.sqlite_path)
        if path.is_absolute():
            return path
        return (self.project_root / path).resolve()

    @property
    def logs_abspath(self) -> Path:
        path = Path(self.logs_dir)
        if path.is_absolute():
            return path
        return (self.project_root / path).resolve()


settings = Settings()
settings.logs_abspath.mkdir(parents=True, exist_ok=True)
settings.sqlite_abspath.parent.mkdir(parents=True, exist_ok=True)
