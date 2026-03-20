# Documentación explicativa del bloque 3 ASFI

## Propósito
Este documento explica de forma clara qué se hizo en el bloque 3 del proyecto `conversion-monetaria-asfi`, cómo quedó organizado el servicio y dónde está cada parte importante dentro del repositorio.

El bloque 3 representa el servicio central de ASFI. Su responsabilidad es consumir información desde los bancos, interpretar los campos cifrados, descifrarlos con el algoritmo correcto según el banco, consultar el tipo de cambio vigente, convertir saldos en USD a Bs, registrar el resultado en la base central, auditar la operación, devolver la actualización al banco y validar consistencia.

## Alcance de la entrega
La versión consolidada cubre las tareas 1 a 17 e incluye:

- arquitectura modular documentada
- scripts SQL para la base oficial de ASFI
- seed de 14 bancos con su algoritmo de cifrado
- cliente HTTP real y cliente mock
- interpretación de `campos_cifrados`
- registro central de llaves por banco
- descifrado tolerante a errores
- tipo de cambio dinámico configurable
- conversión monetaria con 4 decimales
- código de verificación hexadecimal
- persistencia central de cuentas y auditoría
- callback al banco y validación de consistencia
- ejecución paralela por banco
- escritura por lotes para evitar cuello de botella
- seguridad básica con API key, timestamp, nonce e integridad por hash
- Docker para MySQL y Neo4j
- pruebas automatizadas

## Arquitectura general
La solución se organizó por módulos para evitar un archivo monolítico y para permitir pruebas por partes.

### Módulos principales
1. API y orquestación.
2. Consumo de bancos.
3. Validación de request.
4. Interpretación de `campos_cifrados`.
5. Gestión de llaves.
6. Descifrado.
7. Tipo de cambio.
8. Conversión.
9. Persistencia.
10. Auditoría.
11. Callback al banco.
12. Validación de consistencia.
13. Ejecución paralela.

## Flujo del servicio
1. Se identifica el banco a procesar.
2. Se valida la solicitud.
3. Se obtienen cuentas desde la API del banco.
4. Se lee `campos_cifrados`.
5. Se localiza el algoritmo y la llave del banco.
6. Se descifran solo los campos marcados.
7. Se consulta el tipo de cambio.
8. Se realiza la conversión USD a Bs.
9. Se genera el código de verificación.
10. Se guarda el resultado en ASFI.
11. Se registra auditoría.
12. Se notifica al banco.
13. Se valida consistencia.

## Cobertura de tareas 1 a 17
| Tarea | Qué se hizo | Archivo clave |
|---|---|---|
| 1 | Arquitectura interna | `docs/arquitectura-interna-asfi.md` |
| 2 | Base central ASFI | `sql/01_create_asfi_mysql.sql` |
| 3 | Seed de 14 bancos | `sql/02_seed_bancos.sql` |
| 4 | Consumo de APIs | `app/clients/http_bank_client.py` |
| 5 | Lectura de campos cifrados | `app/crypto/encrypted_fields.py` |
| 6 | Gestión de llaves | `app/crypto/key_registry.py` |
| 7 | Descifrado | `app/crypto/decryptor.py` |
| 8 | Tipo de cambio dinámico | `app/exchange/rate_service.py` |
| 9 | Conversión monetaria | `app/converter/currency.py` |
| 10 | Código de verificación | `app/utils/security.py` |
| 11 | Registro en ASFI | `app/repository/sqlite_repository.py` |
| 12 | Auditoría | `app/audit/logger.py` |
| 13 | Devolución al banco | `app/response/bank_callback.py` |
| 14 | Consistencia | `app/consistency/checker.py` |
| 15 | Barrido paralelo | `app/core/pipeline.py` |
| 16 | Escritura por lotes | `app/repository/sqlite_repository.py` |
| 17 | Seguridad básica | `app/validators/request_validator.py` |

## Base de datos
La base central formal se dejó en MySQL a nivel de script y en SQLite para la demo local. Se respetan las tablas `Bancos` y `Cuentas`, y además se agregan tablas de soporte para auditoría, callbacks, llaves, errores, logs de tipo de cambio y validación de consistencia.

## Seguridad
Se implementó seguridad básica y defendible para la práctica:

- API key por banco
- timestamp
- nonce
- mitigación de replay
- hash de integridad del lote
- control de fuente del tipo de cambio
- asociación banco -> algoritmo -> llave
- actualización del banco por API y no por acceso directo a base de datos

## Rendimiento
El procesamiento se hace en paralelo por banco para reducir el sesgo causado por la fluctuación del tipo de cambio. La capa de persistencia quedó separada y con escritura por lotes en la demo, para que la base central no destruya el paralelismo logrado en la lectura.

## Ejecución
### Demo local
```bash
python scripts/run_demo.py --dataset "../01 - Practica 2 Dataset.csv" --limit 300 --batch-size 100 --rate-mode OFICIAL --interval-seconds 3
```

### API FastAPI
```bash
uvicorn main:app --reload --port 8090
```

### Docker
```bash
docker compose -f docker/docker-compose.asfi.yml up -d
```

## Resumen para defensa
El bloque 3 implementa el servicio central de ASFI. Consume información de los bancos, interpreta campos cifrados, descifra según el algoritmo configurado para cada banco, consulta un tipo de cambio dinámico, realiza la conversión monetaria, persiste el resultado en la base central, audita la operación, devuelve el saldo convertido al banco y valida consistencia. El diseño quedó modular, concurrente y defendible en seguridad básica y rendimiento.

## Conclusión
La entrega final no es solo una colección de scripts. Es un servicio organizado por capas, con documentación, pruebas y preparación para integración con el bloque 2. Esto permite entender el proyecto, ejecutarlo localmente y seguir iterándolo sin rehacer la arquitectura.
