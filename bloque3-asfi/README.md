# Bloque 3 - Servicio ASFI de Conversión Monetaria

Implementación profesional en Python del **bloque 3** del proyecto `conversion-monetaria-asfi`.

Incluye:
- arquitectura modular y documentada
- cliente para consumir APIs bancarias en paralelo
- validación de request con timestamp y nonce
- interpretación de `campos_cifrados`
- registro central de llaves por banco
- módulo de descifrado tolerante a errores
- servicio dinámico de tipo de cambio
- conversión monetaria con precisión de 4 decimales
- persistencia central ASFI en MySQL (scripts) y SQLite (demo local)
- auditoría en archivo y tabla
- devolución al banco y validación de consistencia
- soporte de demo con dataset CSV
- scripts SQL, Docker y material de defensa

## Estructura

```text
bloque3-asfi-entrega/
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

Esto:
1. trunca tablas demo
2. siembra catálogo de bancos
3. procesa cuentas por banco en paralelo
4. genera auditoría y log de tipo de cambio
5. devuelve resultado a bancos mock
6. valida consistencia

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

## Decisiones de diseño

- **Bloque 3 estaba vacío en el repo**, por eso esta entrega crea una base limpia y lista para integrarse.
- Para demo local se usa **SQLite** porque no depende de drivers externos. La entrega incluye los **scripts MySQL** exigidos para producción y defensa.
- El motor de tipo de cambio es **dinámico, configurable y desacoplado** del flujo de conversión.
- La lógica de descifrado usa una **fábrica por algoritmo** y un **registro central de llaves** para evitar acoplamiento y desincronización.
- Se incluye **cliente HTTP real** y **cliente mock**. Así puedes defender el diseño aunque bloque 2 no esté disponible.
- Para algoritmos que no siempre tienen librería nativa disponible en todos los entornos académicos (por ejemplo `DES` y `Twofish`), el proyecto incluye un **modo de compatibilidad controlado** documentado en `docs/decisiones-tecnicas.md`.

## Archivos clave

- `docs/arquitectura-interna-asfi.md`
- `sql/01_create_asfi_mysql.sql`
- `sql/02_seed_bancos.sql`
- `app/core/pipeline.py`
- `app/crypto/decryptor.py`
- `app/clients/mock_bank_client.py`
- `app/exchange/rate_service.py`
- `app/repository/sqlite_repository.py`
- `scripts/run_demo.py`

## Nota importante

No puedo hacer push directo a tu GitHub desde aquí, pero la carpeta y el `.zip` salen listos para que los copies dentro de `bloque3-asfi/` en tu repo.
