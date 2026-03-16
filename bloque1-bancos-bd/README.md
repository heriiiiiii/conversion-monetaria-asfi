# Sistema Bancario Distribuido con Docker 🏦

Simulación de un sistema financiero boliviano con **14 bancos** distribuidos en **5 motores de bases de datos**, orquestados con **Docker Compose**.

---

## 📐 Arquitectura del Sistema

```
┌──────────────────────────────────────────────────────────────┐
│            Base de Datos Central (central_postgres)          │
│         Tablas: bancos · cuentas_global · transacciones      │
└───────┬──────────┬──────────┬────────────┬───────────────────┘
        │          │          │            │
   ┌────▼───┐ ┌────▼───┐ ┌────▼────┐ ┌────▼────┐ ┌─────────┐
   │Postgres│ │ MySQL  │ │ MariaDB │ │ MongoDB │ │  Redis  │
   │ :5433  │ │ :3307  │ │  :3308  │ │ :27017  │ │  :6379  │
   └────┬───┘ └────┬───┘ └────┬────┘ └────┬────┘ └────┬────┘
        │          │          │            │            │
   FIE·PYME  Unión·MSC   BISA·Ganadero  Solidario  Nac.Arg.
   Desarrollo BNB·BCP   Económico·Prodem Fortaleza
```

## 🗂️ Distribución de Bancos

| # | Banco | Algoritmo | Motor | Puerto | Base de Datos |
|---|-------|-----------|-------|--------|---------------|
| 1  | Banco Unión                      | César    | MySQL      | 3307 | `union_banco`      |
| 2  | Banco Mercantil Santa Cruz        | Atbash   | MySQL      | 3307 | `mercantil_banco`  |
| 3  | Banco Nacional de Bolivia (BNB)   | Vigenère | MySQL      | 3307 | `bnb_banco`        |
| 4  | Banco de Crédito de Bolivia (BCP) | Playfair | MySQL      | 3307 | `bcp_banco`        |
| 5  | Banco BISA                        | Hill     | MariaDB    | 3308 | `bisa_banco`       |
| 6  | Banco Ganadero                    | DES      | MariaDB    | 3308 | `ganadero_banco`   |
| 7  | Banco Económico                   | 3DES     | MariaDB    | 3308 | `economico_banco`  |
| 8  | Banco Prodem                      | Blowfish | MariaDB    | 3308 | `prodem_banco`     |
| 9  | Banco Solidario                   | Twofish  | MongoDB    | 27017| `solidario_banco`  |
| 10 | Banco Fortaleza                   | AES      | MongoDB    | 27017| `fortaleza_banco`  |
| 11 | Banco FIE                         | RSA      | PostgreSQL | 5433 | `fie`              |
| 12 | Banco PYME                        | ElGamal  | PostgreSQL | 5433 | `pyme`             |
| 13 | Banco de Desarrollo Productivo    | ECC      | PostgreSQL | 5433 | `desarrollo`       |
| 14 | Banco Nación Argentina            | ChaCha20 | Redis      | 6379 | DB 0               |
| — | **Base Central**                  | —        | PostgreSQL | 5432 | `central_db`       |

---

## 🚀 Cómo levantar el sistema

### Requisitos
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y en ejecución
- Docker Compose v2+

### Levantar todos los contenedores

```bash
docker-compose up -d
```

### Verificar que todos están corriendo

```bash
docker-compose ps
```

Deberías ver **6 contenedores** con estado `Up` (healthy):

```
NAME               IMAGE                STATUS          PORTS
banco_postgres     postgres:15-alpine   Up (healthy)    0.0.0.0:5433->5432/tcp
banco_mysql        mysql:8.0            Up (healthy)    0.0.0.0:3307->3306/tcp
banco_mariadb      mariadb:10.11        Up (healthy)    0.0.0.0:3308->3306/tcp
banco_mongodb      mongo:7.0            Up (healthy)    0.0.0.0:27017->27017/tcp
banco_redis        redis:7.2-alpine     Up (healthy)    0.0.0.0:6379->6379/tcp
central_postgres   postgres:15-alpine   Up (healthy)    0.0.0.0:5432->5432/tcp
```

### Detener el sistema

```bash
docker-compose down
```

### Detener y eliminar volúmenes (borrar todos los datos)

```bash
docker-compose down -v
```

---

## 🔌 Credenciales de Conexión

### PostgreSQL (Bancos FIE, PYME, Desarrollo)
| Parámetro | Valor |
|-----------|-------|
| Host | `localhost` |
| Puerto | `5433` |
| Usuario | `admin` |
| Contraseña | `admin123` |
| Bases de datos | `fie` · `pyme` · `desarrollo` |

### MySQL (Bancos Unión, Mercantil, BNB, BCP)
| Parámetro | Valor |
|-----------|-------|
| Host | `localhost` |
| Puerto | `3307` |
| Usuario | `admin` |
| Contraseña | `admin123` |
| Root contraseña | `root123` |
| Bases de datos | `union_banco` · `mercantil_banco` · `bnb_banco` · `bcp_banco` |

### MariaDB (Bancos BISA, Ganadero, Económico, Prodem)
| Parámetro | Valor |
|-----------|-------|
| Host | `localhost` |
| Puerto | `3308` |
| Usuario | `admin` |
| Contraseña | `admin123` |
| Root contraseña | `root123` |
| Bases de datos | `bisa_banco` · `ganadero_banco` · `economico_banco` · `prodem_banco` |

### MongoDB (Bancos Solidario, Fortaleza)
| Parámetro | Valor |
|-----------|-------|
| URI | `mongodb://admin:admin123@localhost:27017` |
| Bases de datos | `solidario_banco` · `fortaleza_banco` |

### Redis (Banco Nación Argentina)
| Parámetro | Valor |
|-----------|-------|
| Host | `localhost` |
| Puerto | `6379` |
| Contraseña | `admin123` |

### PostgreSQL Central
| Parámetro | Valor |
|-----------|-------|
| Host | `localhost` |
| Puerto | `5432` |
| Usuario | `central_admin` |
| Contraseña | `central123` |
| Base de datos | `central_db` |

---

## 🔍 Comandos de Verificación

### Ver todos los bancos en la base central
```bash
docker exec central_postgres psql -U central_admin -d central_db -c "SELECT * FROM bancos;"
```

### Ver transacciones globales
```bash
docker exec central_postgres psql -U central_admin -d central_db -c "SELECT * FROM transacciones ORDER BY fecha DESC LIMIT 10;"
```

### Ver bases de datos PostgreSQL (bancos)
```bash
docker exec banco_postgres psql -U admin -c "\l"
```

### Ver cuentas de Banco FIE
```bash
docker exec banco_postgres psql -U admin -d fie -c "SELECT id, ci, nombres, apellidos, nro_cuenta, saldo FROM cuentas;"
```

### Ver bases de datos MySQL
```bash
docker exec banco_mysql mysql -uadmin -padmin123 -e "SHOW DATABASES;"
```

### Ver cuentas del Banco Unión (MySQL)
```bash
docker exec banco_mysql mysql -uadmin -padmin123 union_banco -e "SELECT id, ci, nombres, apellidos, nro_cuenta, saldo FROM cuentas;"
```

### Ver bases de datos MariaDB
```bash
docker exec banco_mariadb mysql -uadmin -padmin123 -e "SHOW DATABASES;"
```

### Ver cuentas del Banco BISA (MariaDB)
```bash
docker exec banco_mariadb mysql -uadmin -padmin123 bisa_banco -e "SELECT id, ci, nombres, apellidos, nro_cuenta, saldo FROM cuentas;"
```

### Ver registros en MongoDB
```bash
docker exec banco_mongodb mongosh -u admin -p admin123 --authenticationDatabase admin \
  --eval "use solidario_banco; db.cuentas.find({}, {_id:0, ci:1, nombres:1, nro_cuenta:1, saldo:1}).pretty()"
```

### Ver cuentas en Redis
```bash
# Listar todas las cuentas
docker exec banco_redis redis-cli -a admin123 KEYS "cuenta:*"

# Ver una cuenta específica
docker exec banco_redis redis-cli -a admin123 HGETALL "cuenta:NACIARG-0001"
```

---

## 🌱 Cargar Datos de Prueba Adicionales

### Redis (Banco Nación Argentina)
```bash
# Desde Windows PowerShell:
docker exec banco_redis sh -c "$(cat scripts/seed_redis.sh)"

# O copiar y ejecutar dentro del contenedor:
docker cp scripts/seed_redis.sh banco_redis:/seed_redis.sh
docker exec banco_redis sh /seed_redis.sh
```

### MongoDB (datos adicionales)
```bash
docker cp scripts/seed_mongo.js banco_mongodb:/seed_mongo.js
docker exec banco_mongodb mongosh -u admin -p admin123 --authenticationDatabase admin /seed_mongo.js
```

### Base Central (transacciones adicionales)
```bash
docker exec -i central_postgres psql -U central_admin -d central_db < scripts/seed_data.sql
```

---

## 📁 Estructura del Proyecto

```
BaseD-Practica2/
├── docker-compose.yml          # Orquestación de los 6 contenedores
├── README.md                   # Esta documentación
│
├── bancos/
│   ├── postgres/
│   │   └── init.sql            # FIE (RSA), PYME (ElGamal), Desarrollo (ECC)
│   ├── mysql/
│   │   └── init.sql            # Unión (César), Mercantil (Atbash), BNB (Vigenère), BCP (Playfair)
│   ├── mariadb/
│   │   └── init.sql            # BISA (Hill), Ganadero (DES), Económico (3DES), Prodem (Blowfish)
│   ├── mongodb/
│   │   └── init.js             # Solidario (Twofish), Fortaleza (AES)
│   └── redis/
│       └── redis.conf          # Config Redis + Nación Argentina (ChaCha20)
│
├── central/
│   └── init.sql                # Tablas: bancos, cuentas_global, transacciones
│
└── scripts/
    ├── seed_data.sql           # Transacciones adicionales (base central)
    ├── seed_mongo.js           # Cuentas adicionales MongoDB
    └── seed_redis.sh           # Cuentas Banco Nación Argentina en Redis
```

---

## 🛠️ Troubleshooting

**El contenedor MySQL/MariaDB no arranca:**
```bash
docker logs banco_mysql
docker logs banco_mariadb
```
Asegúrate de que los puertos 3307 y 3308 estén libres.

**Error de contraseña en Redis:**
```bash
docker exec banco_redis redis-cli -a admin123 ping
# Debe responder: PONG
```

**Ver logs en tiempo real:**
```bash
docker-compose logs -f central_postgres
```

**Reiniciar un solo contenedor:**
```bash
docker-compose restart banco_postgres
```
