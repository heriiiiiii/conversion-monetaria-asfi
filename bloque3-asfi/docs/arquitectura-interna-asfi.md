# Arquitectura interna del servicio ASFI

## Flujo interno

1. **Ejecución paralela** dispara el barrido de las 14 APIs bancarias al mismo tiempo.
2. **Consumo de APIs** obtiene los lotes por banco con soporte para autenticación básica, timestamp y nonce.
3. **Validación de request** verifica estructura, ventana temporal y unicidad del nonce.
4. **Interpretación de `campos_cifrados`** identifica únicamente los campos que deben descifrarse.
5. **Descifrado** selecciona algoritmo y llave por `BancoId` desde el registro central.
6. **Tipo de cambio** obtiene una cotización dinámica desde un servicio desacoplado.
7. **Conversión** calcula `SaldoBs = SaldoUSD * TipoCambio` con 4 decimales.
8. **Persistencia ASFI** registra USD, Bs, fecha y código de verificación.
9. **Auditoría** deja traza en archivo y base de datos.
10. **Devolución al banco** envía saldo convertido y código de verificación.
11. **Validación de consistencia** compara respuesta del banco con el registro central.

## Responsabilidad de cada módulo

### `app/clients/`
Cliente HTTP real y cliente mock para integrar bloque 2 o simularlo con dataset.

### `app/validators/`
Valida timestamp, nonce, estructura del lote y precondiciones mínimas del contrato.

### `app/crypto/encrypted_fields.py`
Interpreta `campos_cifrados` y evita descifrar `Nombres`, `Apellidos` y `NroCuenta`.

### `app/crypto/key_registry.py`
Centraliza `BancoId -> algoritmo -> llave`, materializa llaves de demo y registra sincronización.

### `app/crypto/decryptor.py`
Aplica el algoritmo correcto por banco y maneja descifrado campo por campo.

### `app/exchange/rate_service.py`
Genera el tipo de cambio dinámico configurable para modo oficial o referencial.

### `app/converter/currency.py`
Realiza la conversión monetaria uniforme con precisión de 4 decimales.

### `app/repository/`
Persistencia de catálogo, cuentas convertidas, auditoría, callbacks, consistencia y errores.

### `app/audit/logger.py`
Trazabilidad operativa en archivo JSON lineado.

### `app/response/bank_callback.py`
Devuelve al banco el saldo convertido y el código de verificación.

### `app/consistency/checker.py`
Valida que el banco y ASFI manejen el mismo resultado final.

### `app/core/pipeline.py`
Orquesta todo el flujo end-to-end.

## Organización sugerida dentro del repo principal

```text
conversion-monetaria-asfi/
└── bloque3-asfi/
    ├── app/
    ├── docs/
    ├── sql/
    ├── scripts/
    ├── tests/
    ├── docker/
    ├── requirements.txt
    └── main.py
```

## Criterios de defensa técnica

- Evita el antipatrón de “todo en `main.py`”.
- Permite pruebas por módulo.
- Reduce el acoplamiento entre cifrado, red, persistencia y negocio.
- Hace posible cambiar el proveedor de tipo de cambio sin tocar el pipeline.
- Permite correr con cliente HTTP real o con cliente mock.
