from __future__ import annotations

import math
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request, status

from app.core.config import settings
from app.database.db_connector import db_connector
from app.models.schemas import (
    ActualizarSaldoRequest,
    ActualizarSaldoResponse,
    CuentaResponse,
    CuentasPaginadasResponse,
    HealthResponse,
    MetadataResponse,
    PaginacionMetadata,
)

router = APIRouter()


def _coerce_cuenta_id(cuenta_id: str) -> str | int:
    """
    Convierte a int si viene un ID numérico.
    Útil para MySQL / MariaDB / PostgreSQL.
    Para Mongo/Redis puede seguir siendo string.
    """
    if cuenta_id.isdigit():
        try:
            return int(cuenta_id)
        except ValueError:
            return cuenta_id
    return cuenta_id


def _build_campos_cifrados(cuenta: dict[str, Any]) -> list[str]:
    campos: list[str] = []

    if cuenta.get("ci_cifrado"):
        campos.append("CI")

    if cuenta.get("saldo_cifrado"):
        campos.append("SaldoUSD")

    return campos


def _to_cuenta_response(cuenta: dict[str, Any]) -> CuentaResponse:
    return CuentaResponse(
        CuentaId=cuenta.get("id"),
        BancoId=int(cuenta.get("id_banco") or settings.BANCO_ID),
        CI=str(cuenta.get("ci", "")),
        Nombres=str(cuenta.get("nombres", "")),
        Apellidos=str(cuenta.get("apellidos", "")),
        NroCuenta=str(cuenta.get("nro_cuenta", "")),
        SaldoUSD=str(cuenta.get("saldo", "")),
        campos_cifrados=_build_campos_cifrados(cuenta),
    )


@router.get("/cuentas", response_model=CuentasPaginadasResponse)
async def obtener_cuentas(
    request: Request,
    limit: int = Query(default=settings.DEFAULT_LIMIT, ge=1, le=settings.MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
    page: int | None = Query(default=None, ge=1),
):
    """
    Devuelve cuentas del banco en formato uniforme hacia ASFI.

    Importante:
    - NO recifra datos.
    - Solo expone lo que ya existe en la base del bloque 1.
    - Usa las banderas ci_cifrado y saldo_cifrado para informar qué campos están cifrados.
    """
    try:
        if page is not None:
            offset = (page - 1) * limit

        total_registros = db_connector.count_cuentas()
        cuentas = db_connector.get_cuentas(limit=limit, offset=offset)

        data = [_to_cuenta_response(cuenta) for cuenta in cuentas]

        total_paginas = math.ceil(total_registros / limit) if limit > 0 else 1
        pagina_actual = (offset // limit) + 1 if limit > 0 else 1
        hay_mas = (offset + len(data)) < total_registros

        return CuentasPaginadasResponse(
            data=data,
            paginacion=PaginacionMetadata(
                total_registros=total_registros,
                registros_devueltos=len(data),
                limit=limit,
                offset=offset,
                pagina_actual=pagina_actual,
                total_paginas=total_paginas,
                hay_mas=hay_mas,
            ),
            metadata=MetadataResponse(
                total_cuentas=total_registros,
                banco_nombre=settings.BANCO_NOMBRE,
                algoritmo_cifrado=settings.ENCRYPTION_ALGORITHM,
            ),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener cuentas: {str(e)}",
        )


@router.put("/cuentas/{cuenta_id}/actualizar-saldo", response_model=ActualizarSaldoResponse)
async def actualizar_saldo_cuenta(
    cuenta_id: str,
    payload: ActualizarSaldoRequest,
    request: Request,
):
    """
    Actualiza saldo_bs y code_verif de una cuenta.
    Este endpoint corresponde al contrato banco <- ASFI.
    """
    try:
        cuenta_id_real = _coerce_cuenta_id(cuenta_id)

        cuenta = db_connector.get_cuenta_by_id(cuenta_id_real)
        if cuenta is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cuenta no encontrada: {cuenta_id}",
            )

        if payload.SaldoBs <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SaldoBs debe ser mayor a 0",
            )

        if not payload.CodigoVerificacion or len(payload.CodigoVerificacion.strip()) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CodigoVerificacion debe tener al menos 6 caracteres",
            )

        actualizado = db_connector.actualizar_saldo(
            cuenta_id=cuenta_id_real,
            saldo_bs=payload.SaldoBs,
            code_verif=payload.CodigoVerificacion,
        )

        if not actualizado:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo actualizar la cuenta",
            )

        fecha_actualizacion = payload.FechaActualizacion or datetime.utcnow()

        return ActualizarSaldoResponse(
            mensaje="Cuenta actualizada exitosamente",
            cuenta_id=cuenta_id,
            saldo_bs_actualizado=payload.SaldoBs,
            codigo_verificacion=payload.CodigoVerificacion,
            fecha_actualizacion=fecha_actualizacion,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar saldo: {str(e)}",
        )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    try:
        db_status = db_connector.test_connection()

        return HealthResponse(
            status="healthy" if db_status else "degraded",
            banco_id=settings.BANCO_ID,
            timestamp=datetime.utcnow(),
            version=settings.API_VERSION,
            database_connected=db_status,
        )
    except Exception:
        return HealthResponse(
            status="unhealthy",
            banco_id=settings.BANCO_ID,
            timestamp=datetime.utcnow(),
            version=settings.API_VERSION,
            database_connected=False,
        )


@router.get("/configuracion")
async def get_configuracion():
    return {
        "banco_id": settings.BANCO_ID,
        "banco_nombre": settings.BANCO_NOMBRE,
        "api_version": settings.API_VERSION,
        "motor_bd": settings.DB_ENGINE,
        "algoritmo_cifrado": settings.ENCRYPTION_ALGORITHM,
        "tabla_o_coleccion": settings.DB_TABLE if settings.DB_ENGINE.lower() != "mongodb" else settings.MONGODB_COLLECTION,
        "politica_cifrado": {
            "CI": "se expone como está almacenado en BD",
            "SaldoUSD": "se expone como está almacenado en BD",
            "campos_cifrados": "se informan usando ci_cifrado y saldo_cifrado",
        },
        "actualizacion_permitida": {
            "campo_saldo_bs": settings.FIELD_SALDO_BS,
            "campo_code_verif": settings.FIELD_CODE_VERIF,
        },
    }