# Documentación Breve — Bloque 1

Este documento sintetiza la información solicitada en el Entregable 6 del Bloque 1.

## 1. Decisiones Tomadas

- **Consolidación de Contenedores:** Para evitar saturar el sistema con 14 contenedores de bases de datos diferentes, se decidió agrupar los bancos por motor. Se utilizan 5 contenedores principales (MySQL, MariaDB, PostgreSQL, MongoDB, Redis) que alojan las 14 bases de datos lógicas. Esto optimiza el consumo de memoria y recursos, cumpliendo con la regla de 14 bases de datos diferentes pero haciéndolo viable en una máquina local.
- **Implementación de Cifrado:** El cifrado simulado académico se implementó usando el patrón `base64(ALGORITMO::valor)`. La política de cifrado selectivo se aplica durante el proceso del dataset en Python (`process_csv.py`), garantizando uniformidad antes de generar los scripts SQL, JS y SH de inserción.
- **Nomenclatura Uniforme:** Las bases de datos y colecciones respetan un formato claro, por ejemplo `banco_union`, `banco_bnb`, y las tablas/colecciones se llaman `cuentas` en todos los casos (excepto en Redis, que es clave-valor tipo HASH global).
- **Campos Adicionales:** Se añadieron booleanos `ci_cifrado` y `saldo_cifrado` a la estructura de las tablas para que el equipo de APIs (Bloque 2) sepa rápidamente si el dato que están leyendo debe ser descifrado o no, según los umbrales.
- **Campos Nulos:** Se respetó estrictamente que `saldo_bs` y `code_verif` inicien como nulos en todas las bases, permitiendo que la API o un proceso posterior los llene.

## 2. Problemas Encontrados y Resoluciones

- **Diferencias de Sintaxis de Inserción:** Los motores NoSQL (MongoDB y Redis) no usan el estándar SQL. Se solucionó con el script `process_csv.py` generando archivos JS (`insertMany()`) para MongoDB y scripts de consola `redis-cli HSET` para Redis.
- **Incompatibilidad de Nombres de Columnas:** Las bases relacionales usan nombres de columna estandarizados como `nro_cuenta`, mientras que en MongoDB el identificador es `_id` por defecto. Se adaptó cada generador de consultas para respetar la estructura solicitada de `CuentaId` a nivel lógico. `id` (int/serial) en relacionales, `_id` en Mongo, y llave `cuenta:{nro_cuenta}` en Redis.

## 3. Supuestos Realizados

- **Cifrado Académico:** Se asume que el cifrado es un proceso simulado mediante codificación "base64" que adjunta el nombre del algoritmo para evidenciar el control por parte del Bloque 1. En producción, la API (Bloque 2) simularía el proceso de descifrado cortando el prefijo.
- **Id_Banco:** Se asume que los 14 bancos están debidamente referenciados por sus IDs del 1 al 14 dentro del archivo CSV (`dataset_base.csv`).
- **Base Central:** Se supuso la necesidad de una base de datos central en PostgreSQL (`central_postgres`) para futuras tareas de consolidación por parte de ASFI, aunque el dataset inicial sólo popule los bancos.

## 4. Pendientes (Para el Bloque 2 - APIs)

- **Desarrollo de Endpoints:** El equipo de APIs debe leer `docs/api_config.json` para conectarse a cada uno de los 14 bancos y crear un API Gateway o 14 servicios independientes.
- **Lógica de Descifrado:** Se debe programar la lectura de las banderas `ci_cifrado` y `saldo_cifrado` para descifrar dinámicamente los campos devueltos en peticiones GET.
- **Conversión Monetaria ASFI:** Deberán implementar el módulo que llame a la base, verifique que `saldo_bs` está nulo, lea `saldo` en USD, aplique la tasa de cambio y actualice la fila poblada, llenando además `code_verif`.
