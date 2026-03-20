from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Any, Dict, List, Literal, Optional

from pydantic import BaseModel, BeforeValidator, Field


def _normalize_account_id(value: Any) -> str:
    if value is None:
        raise ValueError("cuenta_id no puede ser nulo")
    return str(value)


AccountId = Annotated[str, BeforeValidator(_normalize_account_id)]


class EncryptedEnvelope(BaseModel):
    algorithm: str
    ciphertext: str
    original_length: int
    iv: Optional[str] = None
    nonce: Optional[str] = None
    tag: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BankAccountPayload(BaseModel):
    banco_id: int
    banco_nombre: str
    algoritmo: str
    cuenta_id: AccountId
    identificacion: Any
    nombres: str
    apellidos: str
    nro_cuenta: str
    saldo_usd: Any
    campos_cifrados: List[str] = Field(default_factory=list)
    timestamp: str
    nonce: str
    lote_id: str


class BankBatchResponse(BaseModel):
    banco_id: int
    banco_nombre: str
    algoritmo: str
    lote_id: str
    timestamp: str
    nonce: str
    cuentas: List[BankAccountPayload]
    api_key: Optional[str] = None
    request_hash: Optional[str] = None


class DecryptedAccountRecord(BaseModel):
    banco_id: int
    banco_nombre: str
    algoritmo: str
    cuenta_id: AccountId
    identificacion: Any
    nombres: str
    apellidos: str
    nro_cuenta: str
    saldo_usd: Decimal
    campos_cifrados: List[str]
    lote_id: str


class RateQuote(BaseModel):
    mode: Literal["OFICIAL", "REFERENCIAL"]
    rate: Decimal
    generated_at: str
    slot: int
    base_rate: Decimal
    drift: Decimal
    source: str = "ASFI_BCB_INTERNAL"


class ConversionRecord(BaseModel):
    cuenta_id: AccountId
    banco_id: int
    banco_nombre: str
    saldo_usd: Decimal
    saldo_bs: Decimal
    fecha_conversion: str
    codigo_verificacion: str
    tipo_cambio: Decimal
    modo_tipo_cambio: str
    fuente_tipo_cambio: str = "ASFI_BCB_INTERNAL"
    lote_id: str
    identificacion: Optional[str] = None
    nro_cuenta: Optional[str] = None


class ProcessingError(BaseModel):
    banco_id: int
    cuenta_id: Optional[AccountId]
    stage: str
    error: str
    lote_id: Optional[str] = None


class AuditEvent(BaseModel):
    timestamp: str
    banco_id: int
    cuenta_id: Optional[AccountId]
    evento: str
    detalle: str
    tipo_cambio: Optional[str] = None
    modo_tipo_cambio: Optional[str] = None
    fuente_tipo_cambio: Optional[str] = None
    lote_id: Optional[str] = None


class CallbackResult(BaseModel):
    banco_id: int
    cuenta_id: AccountId
    accepted: bool
    saldo_bs: Decimal
    codigo_verificacion: str
    updated_at: str


class ConsistencyResult(BaseModel):
    banco_id: int
    cuenta_id: AccountId
    is_consistent: bool
    details: str


class BankProcessingSummary(BaseModel):
    banco_id: int
    banco_nombre: str
    algoritmo: str
    processed_accounts: int = 0
    successful_accounts: int = 0
    failed_accounts: int = 0
    batches_processed: int = 0
    started_at: str
    finished_at: Optional[str] = None
    errors: List[ProcessingError] = Field(default_factory=list)


class RunSummary(BaseModel):
    total_banks: int
    total_accounts: int
    total_successful: int
    total_failed: int
    started_at: str
    finished_at: str
    bank_summaries: List[BankProcessingSummary]