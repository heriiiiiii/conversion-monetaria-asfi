# Sistema Bancario Distribuido con Docker 🏦 — Bloque 1 Completo

Sistema académico que simula **14 bancos** distribuidos en **5 motores** de bases de datos relacionales y NoSQL, junto con una **Base de Grafos (Neo4j)** y una **Base Central de consolidación**. Todo orquestado con Docker Compose.

---

## 📐 Arquitectura Extendida

```text
┌────────────────────────────────────────────────────────────────────────┐
│               Base de Datos Central (central_postgres)                 │
│             Tablas: bancos · cuentas_global · transacciones            │
└───────┬──────────┬──────────┬────────────┬────────────┬────────────┬───┘
        │          │          │            │            │            │
   ┌────▼───┐ ┌────▼───┐ ┌────▼────┐ ┌─────▼───┐   ┌────▼────┐  ┌────▼────┐
   │Postgres│ │ MySQL  │ │ MariaDB │ │ MongoDB │   │  Redis  │  │  Neo4j  │
   │ :5433  │ │ :3307  │ │  :3308  │ │ :27017  │   │  :6379  │  │7474/7687│
   └────┬───┘ └────┬───┘ └────┬────┘ └─────┬───┘   └────┬────┘  └────┬────┘
        │          │          │            │            │            │
   FIE·PYME  Unión·MSC   BISA·Ganadero  Solidario    Nac.Arg.   Grafo de
   Desarrollo BNB·BCP   Económico·Prodem Fortaleza              Relaciones
                                                               (Cliente→Cuenta)
```

## 🗂️ Distribución de Bancos y Algoritmos

El sistema implementa una **política de cifrado selectivo**:
- **CI**: Siempre cifrado.
- **Saldo**: Cifrado solo si *≥ 100,000 USD*.

| # | Banco | Algoritmo | Motor | Puerto | Base de Datos |
|---|-------|-----------|-------|--------|---------------|
| 1  | Banco Unión                      | César    | MySQL      | 3307 | `banco_union`      |
| 2  | Banco Mercantil Santa Cruz        | Atbash   | MySQL      | 3307 | `banco_mercantil_santa_cruz`  |
| 3  | Banco Nacional de Bolivia (BNB)   | Vigenère | MySQL      | 3307 | `banco_bnb`        |
| 4  | Banco de Crédito de Bolivia (BCP) | Playfair | MySQL      | 3307 | `banco_bcp`        |
| 5  | Banco BISA                        | Hill     | MariaDB    | 3308 | `banco_bisa`       |
| 6  | Banco Ganadero                    | DES      | MariaDB    | 3308 | `banco_ganadero`   |
| 7  | Banco Económico                   | 3DES     | MariaDB    | 3308 | `banco_economico`  |
| 8  | Banco Prodem                      | Blowfish | MariaDB    | 3308 | `banco_prodem`     |
| 9  | Banco Solidario                   | Twofish  | MongoDB    | 27017| `banco_solidario`  |
| 10 | Banco Fortaleza                   | AES      | MongoDB    | 27017| `banco_fortaleza`  |
| 11 | Banco FIE                         | RSA      | PostgreSQL | 5433 | `banco_fie`              |
| 12 | Banco PYME                        | ElGamal  | PostgreSQL | 5433 | `banco_pyme`             |
| 13 | Banco de Desarrollo Productivo    | ECC      | PostgreSQL | 5433 | `banco_desarrollo_productivo`       |
| 14 | Banco Nación Argentina            | ChaCha20 | Redis      | 6379 | `DB 0`               |
| —  | **Base Central**                  | —        | PostgreSQL | 5432 | `central_db`       |
| —  | **Grafos (Relaciones)**           | —        | Neo4j      | 7474 | `neo4j`            |

---

## 🚀 Operación del Sistema (Tareas 5-10)

### 1. Levantar contenedores
```bash
docker-compose up -d
```
Verifica que los 7 servicios (`banco_postgres`, `banco_mysql`, `banco_mariadb`, `banco_mongodb`, `banco_redis`, `banco_neo4j`, `central_postgres`) estén en estado `Up`.

### 2. Truncar las 14 Bases de Datos (Reset)
Ejecuta esto para borrar todos los datos de las tablas `cuentas` en todos los bancos. No destruye la estructura, solo los datos.
```bash
bash scripts/reset.sh
```

### 3. Procesar CSV y Repoblar Bases (Populate)
Lee el `data/dataset_base.csv` (70 registros), aplica cifrado selectivo automáticamente y distribuye los registros a los 14 motores + Neo4j.
```bash
bash scripts/populate.sh
```

### 4. Validar Carga de Datos
Verifica el conteo, campos nulos (`saldo_bs`, `codigo_verificacion`) y correctitud del cifrado en los 14 bancos y Neo4j.
```bash
bash scripts/validate.sh
```

---

## 🔗 Entregables para Equipo de APIs (Bloque 2)

**El archivo clave para el siguiente equipo es:**
📄 `docs/api_config.json`

Contiene un mapa técnico exhaustivo con:
- Host, puertos y credenciales para los 14 bancos.
- Nombre exacto de bases de datos y colecciones.
- Estructura de campos (`ci_cifrado`, `saldo_cifrado`, `saldo_bs` que empieza en `NULL`).
- Algoritmo de cifrado utilizado por cada banco.
- Conexión a Neo4j y Base Central.

---

## 🔌 Conexiones Directas (Ejemplos)

### PostgreSQL (Ej: Banco FIE / PYME)
```bash
docker exec banco_postgres psql -U admin -d banco_fie -c "SELECT * FROM cuentas LIMIT 2;"
```

### MySQL / MariaDB (Ej: Banco Unión / BISA)
```bash
docker exec banco_mysql mysql -uadmin -padmin123 banco_union -e "SELECT ci, ci_cifrado, saldo, saldo_cifrado FROM cuentas;"
```

### MongoDB (Ej: Banco Solidario)
```bash
docker exec banco_mongodb mongosh -u admin -p admin123 --authenticationDatabase admin --quiet --eval "use banco_solidario; db.cuentas.find().pretty()"
```

### Neo4j (Explorador Gráfico)
1. Abrir navegador en http://localhost:7474
2. **Usuario:** `neo4j` | **Password:** `admin123`
3. Ejecutar query de ejemplo:
```cypher
MATCH (c:Cliente)-[:TIENE_CUENTA]->(ct:Cuenta)-[:PERTENECE_A]->(b:Banco) RETURN c, ct, b LIMIT 15
```

---

## 🛠️ Estructura del Proyecto

```text
bloque1-bancos-bd/
├── docker-compose.yml          # Orquestación (7 contenedores)
├── README.md                   # Esta documentación
├── data/
│   ├── dataset_base.csv        # Dataset original (70 cuentas)
│   └── processed/              # SQL/JS/SH generados por el script python
├── bancos/                     
│   ├── postgres/init.sql       # Tablas de FIE, PYME, Desarrollo (RSA, ElGamal, ECC)
│   ├── mysql/init.sql          # Tablas Unión, Mercantil, BNB, BCP
│   ├── mariadb/init.sql        # Tablas BISA, Ganadero, Económico, Prodem
│   ├── mongodb/init.js         # Colecciones Solidario, Fortaleza
│   ├── redis/redis.conf        # Config Redis
│   └── neo4j/init.cypher       # Nodos y relaciones iniciales de grafos
├── central/
│   └── init.sql                # Base de datos consolidadora
├── scripts/
│   ├── process_csv.py          # Script de cifrado selectivo y SQL gen
│   ├── reset.sh                # Trunca todas las bases
│   ├── populate.sh             # Repobla todas las bases
│   └── validate.sh             # Verifica coherencia post-carga
└── docs/
    └── api_config.json         # Configuración técnica completa para APIs (Bloque 2)
```
