from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa

from app.constants import BANK_CATALOG, BANK_BY_ID
from app.config import settings


@dataclass(slots=True)
class KeyMaterial:
    bank_id: int
    algorithm: str
    key_type: str
    params: Dict[str, Any]


class KeyRegistry:
    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path = config_path or (settings.project_root / "data" / "key_registry.json")
        self.runtime_dir = settings.project_root / "data" / "generated_keys"
        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        self._config = self._load_config()
        self._cache: dict[int, KeyMaterial] = {}

    def _load_config(self) -> dict[str, Any]:
        with self.config_path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def get(self, bank_id: int) -> KeyMaterial:
        if bank_id in self._cache:
            return self._cache[bank_id]
        row = self._config[str(bank_id)]
        algorithm = BANK_BY_ID[bank_id]["algorithm"]
        key_type = BANK_BY_ID[bank_id]["key_type"]
        params = dict(row)
        params["derived_key"] = base64.b64encode(
            hashlib.sha256(f"{bank_id}:{algorithm}:{row['seed']}".encode("utf-8")).digest()
        ).decode("ascii")
        if algorithm == "RSA":
            params.update(self._load_or_generate_rsa(bank_id))
        elif algorithm == "ECC":
            params.update(self._load_or_generate_ecc(bank_id))
        self._cache[bank_id] = KeyMaterial(
            bank_id=bank_id,
            algorithm=algorithm,
            key_type=key_type,
            params=params,
        )
        return self._cache[bank_id]

    def _load_or_generate_rsa(self, bank_id: int) -> dict[str, str]:
        private_path = self.runtime_dir / f"bank_{bank_id}_rsa_private.pem"
        public_path = self.runtime_dir / f"bank_{bank_id}_rsa_public.pem"
        if not private_path.exists() or not public_path.exists():
            private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            public_key = private_key.public_key()
            private_path.write_bytes(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )
            public_path.write_bytes(
                public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                )
            )
        return {
            "private_key_pem": private_path.read_text(encoding="utf-8"),
            "public_key_pem": public_path.read_text(encoding="utf-8"),
        }

    def _load_or_generate_ecc(self, bank_id: int) -> dict[str, str]:
        private_path = self.runtime_dir / f"bank_{bank_id}_ecc_private.pem"
        public_path = self.runtime_dir / f"bank_{bank_id}_ecc_public.pem"
        if not private_path.exists() or not public_path.exists():
            private_key = ec.generate_private_key(ec.SECP256R1())
            public_key = private_key.public_key()
            private_path.write_bytes(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )
            public_path.write_bytes(
                public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                )
            )
        return {
            "private_key_pem": private_path.read_text(encoding="utf-8"),
            "public_key_pem": public_path.read_text(encoding="utf-8"),
        }

    def export_mapping(self) -> list[dict[str, Any]]:
        result = []
        for bank in BANK_CATALOG:
            material = self.get(bank["bank_id"])
            result.append(
                {
                    "bank_id": bank["bank_id"],
                    "name": bank["name"],
                    "algorithm": bank["algorithm"],
                    "key_type": bank["key_type"],
                    "seed": material.params["seed"],
                }
            )
        return result
