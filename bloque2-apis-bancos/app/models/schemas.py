from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CuentaResponse(BaseModel):
    CuentaId: str | int
    BancoId: int
    CI: str
    Nombres: str
    Apellidos: str
    NroCuenta: str
    SaldoUSD: str
    campos_cifrados: List[str] = Field(default_factory=list)


class MetadataResponse(BaseModel):
    total_cuentas: int
    banco_nombre: str
    algoritmo_cifrado: str


class PaginacionMetadata(BaseModel):
    total_registros: int
    registros_devueltos: int
    limit: int
    offset: int
    pagina_actual: int
    total_paginas: int
    hay_mas: bool


class CuentasPaginadasResponse(BaseModel):
    data: List[CuentaResponse]
    paginacion: PaginacionMetadata
    metadata: MetadataResponse


class ActualizarSaldoRequest(BaseModel):
    SaldoBs: float
    CodigoVerificacion: str
    FechaActualizacion: Optional[datetime] = None


class ActualizarSaldoResponse(BaseModel):
    mensaje: str
    cuenta_id: str | int
    saldo_bs_actualizado: float
    codigo_verificacion: str
    fecha_actualizacion: datetime


class HealthResponse(BaseModel):
    status: str
    banco_id: int
    timestamp: datetime
    version: str
    database_connected: bool