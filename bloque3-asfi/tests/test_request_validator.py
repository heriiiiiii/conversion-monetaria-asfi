import unittest
from pathlib import Path

from app.clients.mock_bank_client import MockBankClient
from app.crypto.key_registry import KeyRegistry
from app.validators.request_validator import RequestValidator


class RequestValidatorTest(unittest.IsolatedAsyncioTestCase):
    async def test_mock_batch_passes_integrity_and_api_key(self):
        dataset = Path(__file__).resolve().parents[2] / '01 - Practica 2 Dataset.csv'
        if not dataset.exists():
            self.skipTest('Dataset no disponible en el entorno de prueba')
        client = MockBankClient(dataset_path=dataset, key_registry=KeyRegistry())
        validator = RequestValidator()
        async for batch in client.fetch_bank_batches(bank_id=1, batch_size=5, limit=5):
            validator.validate_batch(batch)
            break


if __name__ == '__main__':
    unittest.main()
