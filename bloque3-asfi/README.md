# Bloque 3 - Servicio ASFI de Conversión Monetaria

Implementación profesional en Python del **bloque 3** del proyecto `conversion-monetaria-asfi`, con cobertura integrada de las **tareas 1 a 17**.

## Qué incluye

- arquitectura modular documentada
- consumo de APIs bancarias con cliente real HTTP y mock de laboratorio
- validación de request con **API key**, **timestamp**, **nonce** e **integridad por hash**
- interpretación de `campos_cifrados`
- registro central de llaves por banco
- descifrado tolerante a errores
- servicio dinámico de tipo de cambio desacoplado del flujo principal
- conversión monetaria con precisión de 4 decimales
- persistencia central ASFI con esquema oficial `Bancos` + `Cuentas`
- tablas de soporte para auditoría, callbacks, consistencia, llaves y errores
- escritura **por lotes** sobre la base demo para evitar cuello de botella
- devolución al banco vía API y validación de consistencia
- Docker para MySQL y Neo4j
- pruebas automatizadas, scripts de demo y material de defensa

## Cobertura de tareas

Resumen rápido:

- **Tareas 1–10**: arquitectura, esquema central, catálogo de bancos, cliente bancario, `campos_cifrados`, llaves, descifrado, tipo de cambio, conversión y código de verificación.
- **Tareas 11–17**: persistencia ASFI, auditoría, callback al banco, consistencia, barrido paralelo, mitigación de cuello de botella en base y seguridad básica.

Mapa completo:
- `docs/arquitectura-interna-asfi.md`
- `docs/decisiones-tecnicas.md`
- `docs/cobertura-tareas-1-17.md`

## Estructura

```text
bloque3-asfi/
├── app/
├── data/
├── docker/
├── docs/
├── logs/
├── scripts/
├── sql/
├── tests/
├── main.py
└── requirements.txt
```

## Cómo correr localmente

### 1) Demo rápida sobre SQLite

```bash
python scripts/run_demo.py \
  --dataset "../01 - Practica 2 Dataset.csv" \
  --limit 300 \
  --batch-size 100 \
  --rate-mode OFICIAL \
  --interval-seconds 3
```

La demo:
1. trunca tablas demo
2. siembra el catálogo de bancos y llaves
3. procesa cuentas por banco en paralelo
4. registra auditoría y tipo de cambio
5. devuelve resultado al banco mock
6. valida consistencia entre callback y ASFI

### 2) Levantar API FastAPI

```bash
uvicorn main:app --reload --port 8090
```

Endpoints útiles:
- `GET /health`
- `GET /api/v1/exchange-rate/current?mode=OFICIAL`
- `POST /api/v1/process/all`
- `POST /api/v1/process/bank/{bank_id}`
- `GET /api/v1/audit/recent`

### 3) Base central MySQL + Neo4j con Docker

```bash
docker compose -f docker/docker-compose.asfi.yml up -d
```

Después ejecutar:
- `sql/01_create_asfi_mysql.sql`
- `sql/02_seed_bancos.sql`
- `sql/03_create_support_tables.sql`
- `sql/04_consultas_entregable.sql`
- `sql/05_neo4j_seed.cypher`

## Archivos clave

- `docs/arquitectura-interna-asfi.md`
- `docs/cobertura-tareas-1-17.md`
- `sql/01_create_asfi_mysql.sql`
- `sql/02_seed_bancos.sql`
- `sql/03_create_support_tables.sql`
- `app/core/pipeline.py`
- `app/validators/request_validator.py`
- `app/repository/sqlite_repository.py`
- `app/clients/http_bank_client.py`
- `app/clients/mock_bank_client.py`
- `app/exchange/rate_service.py`
- `scripts/run_demo.py`


