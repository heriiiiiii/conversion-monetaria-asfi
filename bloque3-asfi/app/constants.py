from __future__ import annotations

BANK_CATALOG = [
    {"bank_id": 1, "name": "Banco Unión S.A.", "algorithm": "Cesar", "key_type": "symmetric"},
    {"bank_id": 2, "name": "Banco Mercantil Santa Cruz S.A.", "algorithm": "Atbash", "key_type": "symmetric"},
    {"bank_id": 3, "name": "Banco Nacional de Bolivia S.A. (BNB)", "algorithm": "Vigenere", "key_type": "symmetric"},
    {"bank_id": 4, "name": "Banco de Crédito de Bolivia S.A. (BCP)", "algorithm": "Playfair", "key_type": "symmetric"},
    {"bank_id": 5, "name": "Banco BISA S.A.", "algorithm": "Hill", "key_type": "symmetric"},
    {"bank_id": 6, "name": "Banco Ganadero S.A.", "algorithm": "DES", "key_type": "symmetric"},
    {"bank_id": 7, "name": "Banco Económico S.A.", "algorithm": "3DES", "key_type": "symmetric"},
    {"bank_id": 8, "name": "Banco Prodem S.A.", "algorithm": "Blowfish", "key_type": "symmetric"},
    {"bank_id": 9, "name": "Banco Solidario S.A.", "algorithm": "Twofish", "key_type": "symmetric"},
    {"bank_id": 10, "name": "Banco Fortaleza S.A.", "algorithm": "AES", "key_type": "symmetric"},
    {"bank_id": 11, "name": "Banco FIE S.A.", "algorithm": "RSA", "key_type": "asymmetric"},
    {"bank_id": 12, "name": "Banco PYME de la Comunidad S.A.", "algorithm": "ElGamal", "key_type": "asymmetric"},
    {"bank_id": 13, "name": "Banco de Desarrollo Productivo S.A.M.", "algorithm": "ECC", "key_type": "asymmetric"},
    {"bank_id": 14, "name": "Banco de la Nación Argentina", "algorithm": "ChaCha20", "key_type": "symmetric"},
]

BANK_BY_ID = {item["bank_id"]: item for item in BANK_CATALOG}
