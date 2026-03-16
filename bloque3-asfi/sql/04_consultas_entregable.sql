USE ASFI_Central;

-- 1. Total de cuentas convertidas por banco
SELECT b.Nombre, COUNT(*) AS TotalCuentas
FROM Cuentas c
JOIN Bancos b ON b.BancoId = c.BancoId
GROUP BY b.Nombre
ORDER BY TotalCuentas DESC;

-- 2. Monto total convertido en Bs. por banco
SELECT b.Nombre, SUM(c.SaldoBs) AS TotalBs
FROM Cuentas c
JOIN Bancos b ON b.BancoId = c.BancoId
GROUP BY b.Nombre
ORDER BY TotalBs DESC;

-- 3. Último tipo de cambio por modo
SELECT Modo, TipoCambio, Timestamp
FROM TipoCambioLog t
WHERE t.Timestamp = (
    SELECT MAX(t2.Timestamp) FROM TipoCambioLog t2 WHERE t2.Modo = t.Modo
);

-- 4. Errores por etapa
SELECT Etapa, COUNT(*) AS TotalErrores
FROM ProcesamientoErrores
GROUP BY Etapa
ORDER BY TotalErrores DESC;

-- 5. Cuentas con inconsistencia detectada
SELECT *
FROM ConsistencyChecks
WHERE IsConsistent = 0;

-- 6. Top 10 cuentas con mayor saldo en Bs.
SELECT c.CuentaId, b.Nombre, c.SaldoUSD, c.SaldoBs, c.CodigoVerificacion
FROM Cuentas c
JOIN Bancos b ON b.BancoId = c.BancoId
ORDER BY c.SaldoBs DESC
LIMIT 10;

-- 7. Auditoría por cuenta
SELECT *
FROM AuditLog
WHERE CuentaId = 6490024209780150
ORDER BY Timestamp DESC;

-- 8. Bancos y algoritmo asociado
SELECT BancoId, Nombre, AlgoritmoEncriptacion
FROM Bancos
ORDER BY BancoId;
