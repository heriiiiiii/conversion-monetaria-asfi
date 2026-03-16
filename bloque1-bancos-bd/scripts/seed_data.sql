-- =============================================================
-- SEED DATA ADICIONAL — Bancos Relacionales
-- =============================================================
-- Script para ejecutar datos de prueba adicionales
-- en los bancos SQL (PostgreSQL, MySQL, MariaDB).
-- =============================================================

-- ─────────────────────────────────────────
-- INSTRUCCIONES DE USO:
-- ─────────────────────────────────────────
-- PostgreSQL (FIE):
--   docker exec -i banco_postgres psql -U admin -d fie < scripts/seed_data.sql
--
-- MySQL (Unión):
--   docker exec -i banco_mysql mysql -uadmin -padmin123 union_banco < scripts/seed_data.sql
--
-- MariaDB (BISA):
--   docker exec -i banco_mariadb mysql -uadmin -padmin123 bisa_banco < scripts/seed_data.sql
-- ─────────────────────────────────────────

-- ── Transacciones adicionales en la base central ──────────
-- (Ejecutar en central_postgres)
-- docker exec -i central_postgres psql -U central_admin -d central_db < scripts/seed_data.sql

INSERT INTO transacciones (cuenta_origen, cuenta_destino, monto, fecha, estado, descripcion)
SELECT * FROM (VALUES
  ('FIE-100001',   'FIE-100003',    1500.00, NOW() - INTERVAL '10 days', 'COMPLETADA', 'Transferencia interna FIE - cuenta 1 a 3'),
  ('MSC-000001',   'BCP-000001',   25000.00, NOW() - INTERVAL '8 days',  'COMPLETADA', 'Transferencia Mercantil → BCP'),
  ('BNB-000003',   'UNI-000003',    3400.00, NOW() - INTERVAL '7 days',  'COMPLETADA', 'Pago cuota BNB → Unión'),
  ('BISA-000001',  'GAN-000001',    8900.50, NOW() - INTERVAL '6 days',  'COMPLETADA', 'Fondeo BISA → Ganadero'),
  ('ECO-000002',   'PROD-000002',   2200.75, NOW() - INTERVAL '5 days',  'COMPLETADA', 'Pago servicio Económico → Prodem'),
  ('BDP-300003',   'PYME-200003',  50000.00, NOW() - INTERVAL '4 days',  'COMPLETADA', 'Crédito productivo BDP → PYME'),
  ('FORT-000001',  'SOLD-000001',   4100.00, NOW() - INTERVAL '3 days',  'COMPLETADA', 'Transferencia Fortaleza → Solidario'),
  ('NACIARG-0001', 'BNB-000001',   12000.00, NOW() - INTERVAL '2 days',  'PENDIENTE',  'Remesa Nación Argentina → BNB'),
  ('UNI-000001',   'ECO-000001',    6700.00, NOW() - INTERVAL '1 day',   'COMPLETADA', 'Pago nómina Unión → Económico'),
  ('PYME-200001',  'FIE-100001',    9800.00, NOW() - INTERVAL '4 hours', 'COMPLETADA', 'Liquidación PYME → FIE'),
  ('BCP-000002',   'MSC-000002',   17500.00, NOW() - INTERVAL '2 hours', 'RECHAZADA',  'Transferencia rechazada por saldo insuficiente'),
  ('GAN-000001',   'GAN-000002',    3000.00, NOW() - INTERVAL '1 hour',  'COMPLETADA', 'Transferencia interna Ganadero')
) AS v(cuenta_origen, cuenta_destino, monto, fecha, estado, descripcion)
WHERE NOT EXISTS (
  SELECT 1 FROM transacciones
  WHERE transacciones.cuenta_origen = v.cuenta_origen
    AND transacciones.monto = v.monto
    AND transacciones.descripcion = v.descripcion
);
