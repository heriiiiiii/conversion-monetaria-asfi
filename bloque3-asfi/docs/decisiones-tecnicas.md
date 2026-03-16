# Decisiones técnicas y notas de implementación

## 1. Tipo de cambio dinámico desacoplado
No se hardcodea dentro de la conversión. El pipeline consume un servicio independiente con intervalo configurable.

## 2. Lógica de cifrado por estrategia
Cada banco se resuelve por algoritmo configurado, no por `if` gigante dentro del pipeline.

## 3. Gestión de llaves centralizada
`KeyRegistry` evita desincronización porque toda la configuración se consulta en un solo punto.

## 4. Compatibilidad académica para DES y Twofish
En varios entornos de laboratorio no hay soporte nativo uniforme para esas librerías. Por eso:
- `DES` se implementa en modo de compatibilidad reversible controlado.
- `Twofish` se implementa en modo de compatibilidad reversible controlado.

Esto está aislado en `app/crypto/algorithms.py` y se puede sustituir fácilmente si el bloque 2 entrega una librería exacta.

## 5. Justificación de SQLite para demo
Se usa para ejecutar pruebas y smoke tests sin depender de drivers externos. La entrega incluye de todos modos los scripts MySQL exigidos para defensa.

## 6. Pararelismo
El barrido completo se ejecuta con `asyncio.gather`, procesando los 14 bancos de forma concurrente para reducir sesgo temporal por fluctuación del tipo de cambio.

## 7. Cifrado parcial de atributos
Por consigna y por eficiencia, solo se descifran los campos marcados en `campos_cifrados`. El mock cifra siempre `saldo_usd` y cifra `identificacion` solo cuando el saldo supera el umbral configurado.
