from __future__ import annotations
 
from time import perf_counter
from typing import Any, AsyncIterator
from uuid import uuid4
 
import httpx
 
from app.clients.bank_client import AbstractBankClient
from app.core.schemas import BankAccountPayload, BankBatchResponse, CallbackResult
from app.utils.security import derive_bank_api_key
from app.utils.time_utils import utcnow_iso
 
 
class HttpBankClient(AbstractBankClient):
    def __init__(self, endpoints: dict[int, dict[str, Any]], timeout_seconds: int = 20) -> None:
        self.endpoints = endpoints
        self.timeout_seconds = timeout_seconds
 
    async def fetch_bank_batches(
        self,
        bank_id: int,
        batch_size: int = 500,
        limit: int | None = None,
    ) -> AsyncIterator[BankBatchResponse]:
        cfg = self.endpoints[bank_id]
        offset = 0
        remaining = limit
 
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            while True:
                page_limit = batch_size if remaining is None else min(batch_size, remaining)
                if page_limit <= 0:
                    break
 
                params = {
                    "limit": page_limit,
                    "offset": offset,
                }
 
                request_started = perf_counter()
                response = await client.get(
                    cfg["read_url"],
                    params=params,
                    headers=self._build_headers(bank_id, cfg),
                    auth=self._build_auth(cfg),
                )
                request_finished = perf_counter()
                network_time_ms = round((request_finished - request_started) * 1000, 3)
 
                response.raise_for_status()
                payload = response.json()
 
                accounts_raw = payload.get("data", [])
                pagination = payload.get("paginacion", {}) or {}
                metadata = payload.get("metadata", {}) or {}
 
                if not accounts_raw:
                    break
 
                banco_nombre = str(metadata.get("banco_nombre") or cfg.get("bank_name") or f"Banco {bank_id}")
                algoritmo = str(metadata.get("algoritmo_cifrado") or cfg.get("algorithm") or "DESCONOCIDO")
                timestamp = utcnow_iso()
                lote_id = f"bank-{bank_id}-offset-{offset}-limit-{page_limit}-{uuid4().hex[:8]}"
                nonce = uuid4().hex
 
                cuentas = [
                    BankAccountPayload(
                        banco_id=int(item.get("BancoId", bank_id)),
                        banco_nombre=banco_nombre,
                        algoritmo=algoritmo,
                        cuenta_id=str(item.get("CuentaId")),
                        identificacion=item.get("CI"),
                        nombres=str(item.get("Nombres", "")),
                        apellidos=str(item.get("Apellidos", "")),
                        nro_cuenta=str(item.get("NroCuenta", "")),
                        saldo_usd=item.get("SaldoUSD"),
                        campos_cifrados=list(item.get("campos_cifrados", []) or []),
                        timestamp=timestamp,
                        nonce=nonce,
                        lote_id=lote_id,
                    )
                    for item in accounts_raw
                ]
 
                yield BankBatchResponse(
                    banco_id=bank_id,
                    banco_nombre=banco_nombre,
                    algoritmo=algoritmo,
                    lote_id=lote_id,
                    timestamp=timestamp,
                    nonce=nonce,
                    cuentas=cuentas,
                    api_key=cfg.get("api_key", derive_bank_api_key(bank_id)),
                    request_hash=None,
                    network_time_ms=network_time_ms,
                )
 
                fetched_count = len(accounts_raw)
                offset += fetched_count
 
                if remaining is not None:
                    remaining -= fetched_count
                    if remaining <= 0:
                        break
 
                hay_mas = bool(pagination.get("hay_mas"))
                if not hay_mas or fetched_count == 0:
                    break
 
    async def send_callback(self, callback: CallbackResult) -> CallbackResult:
        cfg = self.endpoints[callback.banco_id]
        callback_url = cfg["callback_url"].format(cuenta_id=callback.cuenta_id)
 
        payload = {
            "SaldoBs": float(callback.saldo_bs),
            "CodigoVerificacion": callback.codigo_verificacion,
            "FechaActualizacion": callback.updated_at,
        }
 
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.put(
                callback_url,
                json=payload,
                headers=self._build_headers(callback.banco_id, cfg, include_content_type=True),
                auth=self._build_auth(cfg),
            )
            response.raise_for_status()
 
        return callback
 
    @staticmethod
    def _build_auth(cfg: dict[str, Any]) -> tuple[str, str] | None:
        username = cfg.get("username")
        password = cfg.get("password")
        if username or password:
            return (username or "", password or "")
        return None
 
    @staticmethod
    def _build_headers(
        bank_id: int,
        cfg: dict[str, Any],
        include_content_type: bool = False,
    ) -> dict[str, str]:
        headers: dict[str, str] = {}
 
        api_key = cfg.get("api_key")
        token = cfg.get("token")
 
        if api_key:
            headers["X-API-Key"] = api_key
        elif cfg.get("send_default_api_key", False):
            headers["X-API-Key"] = derive_bank_api_key(bank_id)
 
        if token:
            headers["Authorization"] = f"Bearer {token}"
 
        if include_content_type:
            headers["Content-Type"] = "application/json"
 
        return headers
 