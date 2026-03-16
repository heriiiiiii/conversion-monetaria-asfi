from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from app.config import settings


class AuditLogger:
    def __init__(self) -> None:
        self.log_path = settings.logs_abspath / "audit.log"
        self.logger = logging.getLogger("asfi.audit")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.FileHandler(self.log_path, encoding="utf-8")
            handler.setFormatter(logging.Formatter("%(message)s"))
            self.logger.addHandler(handler)

    def write(self, payload: dict[str, Any]) -> None:
        self.logger.info(json.dumps(payload, ensure_ascii=False))
