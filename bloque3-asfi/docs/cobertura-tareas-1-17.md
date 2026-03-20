# Cobertura de tareas 1 a 17

## Tarea 1. Definir la arquitectura interna del servicio ASFI
- Documento principal: `docs/arquitectura-interna-asfi.md`
- Orquestación técnica: `app/core/pipeline.py`

## Tarea 2. Diseñar la base de datos central de ASFI
- Esquema oficial: `sql/01_create_asfi_mysql.sql`
- Tabla `Bancos` y tabla `Cuentas` respetadas exactamente como en el enunciado.

## Tarea 3. Poblar la tabla Bancos en ASFI
- Seed SQL: `sql/02_seed_bancos.sql`
- Seed demo desde Python: `scripts/seed_bancos.py`

## Tarea 4. Definir cómo ASFI consumirá las APIs de bancos
- Cliente HTTP real: `app/clients/http_bank_client.py`
- Cliente mock para demo y pruebas: `app/clients/mock_bank_client.py`
- Ejecución paralela de bancos: `app/core/pipeline.py`

## Tarea 5. Interpretar correctamente `campos_cifrados`
- Intérprete de campos: `app/crypto/encrypted_fields.py`

## Tarea 6. Gestionar llaves y algoritmo por banco
- Registro central de llaves: `app/crypto/key_registry.py`
- Material de llaves: `data/key_registry.json`, `data/generated_keys/`

## Tarea 7. Implementar el descifrado en ASFI
- Servicio de descifrado: `app/crypto/decryptor.py`
- Implementaciones criptográficas: `app/crypto/algorithms.py`

## Tarea 8. Implementar el servicio de tipo de cambio dinámico
- Servicio desacoplado: `app/exchange/rate_service.py`
- Log de cotizaciones: `TipoCambioLog` en `sql/03_create_support_tables.sql`

## Tarea 9. Implementar la conversión monetaria
- Conversión USD -> Bs: `app/converter/currency.py`

## Tarea 10. Generar el código de verificación
- Utilitario: `app/utils/security.py`
- Integración al flujo: `app/core/pipeline.py`

## Tarea 11. Registrar las conversiones en la base de ASFI
- Persistencia por lotes: `app/repository/sqlite_repository.py`
- Inserta o actualiza `CuentaId`, `BancoId`, `SaldoUSD`, `SaldoBs`, `FechaConversion`, `CodigoVerificacion`.

## Tarea 12. Implementar el log de auditoría
- Tabla `AuditLog`: `sql/03_create_support_tables.sql`
- Logger a archivo: `app/audit/logger.py`
- Registro por operación desde el pipeline: `app/core/pipeline.py`

## Tarea 13. Devolver al banco el saldo convertido y el código
- Servicio de callback: `app/response/bank_callback.py`
- Cliente HTTP y mock: `app/clients/http_bank_client.py`, `app/clients/mock_bank_client.py`

## Tarea 14. Validar consistencia entre banco y ASFI
- Validador: `app/consistency/checker.py`
- Persistencia de resultados: tabla `ConsistencyChecks`

## Tarea 15. Resolver el cuello de botella con barrido paralelo
- Procesamiento concurrente por banco: `app/core/pipeline.py`
- `asyncio.gather(...)` para barrido simultáneo de bancos.

## Tarea 16. Evitar que la base ASFI se vuelva el nuevo cuello de botella
- Escritura por lotes con `executemany`: `app/repository/sqlite_repository.py`
- Ajustes SQLite para laboratorio: WAL, `synchronous=NORMAL`, `temp_store=MEMORY`.
- Persistencia desacoplada del pipeline para poder migrar a repositorio MySQL sin tocar la lógica de negocio.

## Tarea 17. Implementar seguridad básica
- Validación de timestamp, nonce y replay: `app/validators/request_validator.py`
- Validación de API key por banco: `app/validators/request_validator.py`, `app/utils/security.py`
- Validación de integridad del lote con hash: `app/validators/request_validator.py`, `app/utils/security.py`
- Control de fuente del tipo de cambio: `app/exchange/rate_service.py`
- Gestión central de llaves y algoritmo: `app/crypto/key_registry.py`
