import unittest

from app.constants import BANK_CATALOG
from app.crypto.algorithms import decrypt_text, encrypt_text
from app.crypto.key_registry import KeyRegistry


class CryptoRoundtripTest(unittest.TestCase):
    def test_all_bank_algorithms_roundtrip(self):
        registry = KeyRegistry()
        for bank in BANK_CATALOG:
            material = registry.get(bank["bank_id"])
            plaintext = "12345.6789"
            envelope = encrypt_text(bank["algorithm"], plaintext, material)
            decrypted = decrypt_text(bank["algorithm"], envelope, material)
            self.assertEqual(decrypted, plaintext, msg=f"Falló {bank['algorithm']}")


if __name__ == "__main__":
    unittest.main()
