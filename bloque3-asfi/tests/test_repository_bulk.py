import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from app.core.schemas import ConversionRecord
from app.repository.sqlite_repository import AsfiRepository


class RepositoryBulkTest(unittest.TestCase):
    def test_bulk_insert_conversions(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = AsfiRepository(db_path=Path(tmp) / 'test.sqlite3')
            try:
                repo.seed_banks([
                    {'bank_id': 1, 'name': 'Banco Demo', 'algorithm': 'AES', 'seed': 'demo-seed', 'key_type': 'symmetric'}
                ])
                repo.save_conversions_batch([
                    ConversionRecord(
                        cuenta_id=1001,
                        banco_id=1,
                        banco_nombre='Banco Demo',
                        saldo_usd=Decimal('10.0000'),
                        saldo_bs=Decimal('69.6000'),
                        fecha_conversion='2026-03-16T00:00:00+00:00',
                        codigo_verificacion='ABCDEF12',
                        tipo_cambio=Decimal('6.9600'),
                        modo_tipo_cambio='OFICIAL',
                        fuente_tipo_cambio='ASFI_BCB_INTERNAL',
                        lote_id='L1',
                    ),
                    ConversionRecord(
                        cuenta_id=1002,
                        banco_id=1,
                        banco_nombre='Banco Demo',
                        saldo_usd=Decimal('20.0000'),
                        saldo_bs=Decimal('139.2000'),
                        fecha_conversion='2026-03-16T00:00:00+00:00',
                        codigo_verificacion='1234ABCD',
                        tipo_cambio=Decimal('6.9600'),
                        modo_tipo_cambio='OFICIAL',
                        fuente_tipo_cambio='ASFI_BCB_INTERNAL',
                        lote_id='L1',
                    ),
                ])
                self.assertEqual(repo.fetch_account(1001, 1)['SaldoBs'], '69.6000')
                self.assertEqual(repo.fetch_account(1002, 1)['CodigoVerificacion'], '1234ABCD')
            finally:
                repo.close()


if __name__ == '__main__':
    unittest.main()