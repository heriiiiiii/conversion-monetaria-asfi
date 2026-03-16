# Decisiones técnicas y notas de implementación

## 1. Tipo de cambio dinámico desacoplado
No se hardcodea dentro de la conversión. El pipeline consume un servicio independiente con intervalo configurable, modo oficial o referencial y fuente declarada (`ASFI_BCB_INTERNAL`).

## 2. Lógica de cifrado por estrategia
Cada banco se resuelve por algoritmo configurado, no por un `if` gigante dentro del pipeline.

## 3. Gestión de llaves centralizada
`KeyRegistry` evita desincronización porque toda la configuración se consulta en un solo punto y expone el mapa banco -> algoritmo -> llave.

## 4. Compatibilidad académica para DES y Twofish
En varios entornos de laboratorio no hay soporte nativo uniforme para esas librerías. Por eso:
- `DES` se implementa en modo de compatibilidad reversible controlado.
- `Twofish` se implementa en modo de compatibilidad reversible controlado.

Esto está aislado en `app/crypto/algorithms.py` y se puede sustituir si el bloque 2 entrega una implementación exacta distinta.

## 5. Justificación de SQLite para demo
Se usa para pruebas y smoke tests sin depender de drivers externos. La entrega incluye los scripts MySQL exigidos para la base central ASFI y deja la capa de persistencia desacoplada para migrar a MySQL.

## 6. Barrido paralelo
El barrido completo se ejecuta con `asyncio.gather`, procesando los 14 bancos de forma concurrente para reducir sesgo temporal por fluctuación del tipo de cambio.

## 7. Cifrado parcial de atributos
Solo se descifran los campos marcados en `campos_cifrados`. El mock cifra siempre `saldo_usd` y cifra `identificacion` solo cuando el saldo supera el umbral configurado.

## 8. Persistencia por lotes para reducir cuello de botella
La escritura de conversiones, callbacks, auditoría, consistencia y errores usa `executemany` sobre SQLite. Además se habilita WAL, `synchronous=NORMAL` y `temp_store=MEMORY` para que la base demo acompañe el paralelismo.

## 9. Seguridad básica defendible
Se implementa una capa mínima pero defendible para el bloque:
- validación de timestamp
- validación de nonce y mitigación de replay
- validación de API key por banco
- validación de hash de integridad del lote
- control explícito de la fuente del tipo de cambio
- callback por API, no escritura directa en la base del banco

## 10. Consistencia con confirmación del banco
La validación de consistencia compara el registro persistido en ASFI con la confirmación devuelta por el banco (`SaldoBs`, `CodigoVerificacion` y existencia del registro). Si el banco expone un endpoint de relectura en bloque 2, este componente puede ampliarse sin reescribir el resto del flujo.
