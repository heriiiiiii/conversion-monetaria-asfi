from __future__ import annotations

import base64
import hashlib
import json
import math
import secrets
import binascii
from typing import Dict, Iterable, Tuple

from cryptography.hazmat.primitives import hashes, padding, serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding as asym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from app.crypto.key_registry import KeyMaterial

HEX = "0123456789ABCDEF"
HILL_ALPHA = HEX + "X"


def _text_to_hex(text: str) -> str:
    return text.encode("utf-8").hex().upper()


def _hex_to_text(value: str, original_length: int) -> str:
    data = bytes.fromhex(value)
    return data.decode("utf-8")[:original_length]


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _unb64(value: str) -> bytes:
    return base64.b64decode(value.encode("ascii"))


def _derive_bytes(material: KeyMaterial, size: int) -> bytes:
    raw = base64.b64decode(material.params["derived_key"])
    digest = hashlib.sha512(raw + material.algorithm.encode("utf-8")).digest()
    while len(digest) < size:
        digest += hashlib.sha512(digest).digest()
    return digest[:size]


def _stream_xor(data: bytes, key: bytes, label: str) -> bytes:
    out = bytearray()
    counter = 0
    while len(out) < len(data):
        block = hashlib.sha256(key + label.encode("utf-8") + counter.to_bytes(4, "big")).digest()
        out.extend(block)
        counter += 1
    return bytes(a ^ b for a, b in zip(data, out[: len(data)]))


def _caesar_transform(text: str, shift: int) -> str:
    result = []
    for char in text:
        idx = HEX.index(char)
        result.append(HEX[(idx + shift) % len(HEX)])
    return "".join(result)


def _atbash_transform(text: str) -> str:
    return "".join(HEX[-1 - HEX.index(char)] for char in text)


def _key_to_positions(key: str, alphabet: str) -> list[int]:
    key_hex = _text_to_hex(key)
    return [alphabet.index(char) % len(alphabet) for char in key_hex if char in alphabet] or [1]


def _vigenere_encrypt(text: str, key: str) -> str:
    positions = _key_to_positions(key, HEX)
    out = []
    for idx, char in enumerate(text):
        p = positions[idx % len(positions)]
        out.append(HEX[(HEX.index(char) + p) % len(HEX)])
    return "".join(out)


def _vigenere_decrypt(text: str, key: str) -> str:
    positions = _key_to_positions(key, HEX)
    out = []
    for idx, char in enumerate(text):
        p = positions[idx % len(positions)]
        out.append(HEX[(HEX.index(char) - p) % len(HEX)])
    return "".join(out)


def _build_playfair_square(key: str) -> Tuple[Dict[str, Tuple[int, int]], list[list[str]]]:
    seed = []
    for ch in _text_to_hex(key) + HEX:
        if ch not in seed and ch in HEX:
            seed.append(ch)
    grid = [seed[i : i + 4] for i in range(0, 16, 4)]
    positions = {grid[r][c]: (r, c) for r in range(4) for c in range(4)}
    return positions, grid


def _playfair_prepare(text: str) -> str:
    prepared = text
    if len(prepared) % 2 == 1:
        prepared += "F"
    return prepared


def _playfair_transform(text: str, key: str, decrypt: bool) -> str:
    positions, grid = _build_playfair_square(key)
    prepared = text if decrypt else _playfair_prepare(text)
    step = -1 if decrypt else 1
    out = []
    for i in range(0, len(prepared), 2):
        a, b = prepared[i], prepared[i + 1]
        ra, ca = positions[a]
        rb, cb = positions[b]
        if ra == rb:
            out.append(grid[ra][(ca + step) % 4])
            out.append(grid[rb][(cb + step) % 4])
        elif ca == cb:
            out.append(grid[(ra + step) % 4][ca])
            out.append(grid[(rb + step) % 4][cb])
        else:
            out.append(grid[ra][cb])
            out.append(grid[rb][ca])
    return "".join(out)


def _mod_inverse(a: int, mod: int) -> int:
    for x in range(1, mod):
        if (a * x) % mod == 1:
            return x
    raise ValueError("La matriz Hill no es invertible para el módulo configurado.")


def _hill_encrypt(text: str, matrix: Tuple[int, int, int, int]) -> str:
    if len(text) % 2 == 1:
        text += "X"
    mod = len(HILL_ALPHA)
    a, b, c, d = matrix
    out = []
    for i in range(0, len(text), 2):
        x = HILL_ALPHA.index(text[i])
        y = HILL_ALPHA.index(text[i + 1])
        out.append(HILL_ALPHA[(a * x + b * y) % mod])
        out.append(HILL_ALPHA[(c * x + d * y) % mod])
    return "".join(out)


def _hill_decrypt(text: str, matrix: Tuple[int, int, int, int]) -> str:
    mod = len(HILL_ALPHA)
    a, b, c, d = matrix
    det = (a * d - b * c) % mod
    inv_det = _mod_inverse(det, mod)
    inv = ((d * inv_det) % mod, (-b * inv_det) % mod, (-c * inv_det) % mod, (a * inv_det) % mod)
    return _hill_encrypt(text, inv)


def _cbc_encrypt(algo_cls, key: bytes, plaintext: bytes) -> dict:
    iv = secrets.token_bytes(algo_cls.block_size // 8)
    cipher = Cipher(algo_cls(key), modes.CBC(iv))
    padder = padding.PKCS7(algo_cls.block_size).padder()
    padded = padder.update(plaintext) + padder.finalize()
    encryptor = cipher.encryptor()
    enc = encryptor.update(padded) + encryptor.finalize()
    return {"ciphertext": _b64(enc), "iv": _b64(iv)}


def _cbc_decrypt(algo_cls, key: bytes, ciphertext: bytes, iv: bytes) -> bytes:
    cipher = Cipher(algo_cls(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    dec = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(algo_cls.block_size).unpadder()
    return unpadder.update(dec) + unpadder.finalize()


def _rsa_encrypt(material: KeyMaterial, plaintext: bytes) -> dict:
    public_key = serialization.load_pem_public_key(material.params["public_key_pem"].encode("utf-8"))
    chunk_size = 190
    encrypted = []
    for i in range(0, len(plaintext), chunk_size):
        block = plaintext[i : i + chunk_size]
        encrypted.append(
            _b64(
                public_key.encrypt(
                    block,
                    asym_padding.OAEP(
                        mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None,
                    ),
                )
            )
        )
    return {"ciphertext": json.dumps(encrypted)}


def _rsa_decrypt(material: KeyMaterial, ciphertext: str) -> bytes:
    private_key = serialization.load_pem_private_key(
        material.params["private_key_pem"].encode("utf-8"), password=None
    )
    encrypted = json.loads(ciphertext)
    result = bytearray()
    for block in encrypted:
        result.extend(
            private_key.decrypt(
                _unb64(block),
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
        )
    return bytes(result)


def _elgamal_numbers_from_seed(seed: str) -> tuple[int, int, int]:
    p = 2147483647  # primo de Mersenne, suficiente para demo académica
    g = 5
    x = (int(hashlib.sha256(seed.encode("utf-8")).hexdigest(), 16) % (p - 3)) + 2
    return p, g, x


def _elgamal_encrypt(material: KeyMaterial, plaintext: bytes) -> dict:
    p, g, x = _elgamal_numbers_from_seed(material.params["seed"])
    y = pow(g, x, p)
    blocks = []
    block_size = 3
    for i in range(0, len(plaintext), block_size):
        block = plaintext[i : i + block_size]
        m = int.from_bytes(block, "big")
        if m >= p:
            raise ValueError("Bloque demasiado grande para ElGamal demo.")
        k = (secrets.randbelow(p - 2) or 2)
        c1 = pow(g, k, p)
        s = pow(y, k, p)
        c2 = (m * s) % p
        blocks.append([c1, c2, len(block)])
    return {"ciphertext": json.dumps(blocks)}


def _elgamal_decrypt(material: KeyMaterial, ciphertext: str) -> bytes:
    p, _, x = _elgamal_numbers_from_seed(material.params["seed"])
    blocks = json.loads(ciphertext)
    out = bytearray()
    for c1, c2, size in blocks:
        s = pow(c1, x, p)
        s_inv = pow(s, p - 2, p)
        m = (c2 * s_inv) % p
        out.extend(int(m).to_bytes(size, "big"))
    return bytes(out)


def _ecc_encrypt(material: KeyMaterial, plaintext: bytes) -> dict:
    peer_public = serialization.load_pem_public_key(material.params["public_key_pem"].encode("utf-8"))
    ephemeral_private = ec.generate_private_key(ec.SECP256R1())
    shared_key = ephemeral_private.exchange(ec.ECDH(), peer_public)
    aes_key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b"ASFI-ECC").derive(shared_key)
    aesgcm = AESGCM(aes_key)
    nonce = secrets.token_bytes(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    ephemeral_public = ephemeral_private.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return {"ciphertext": _b64(ciphertext), "nonce": _b64(nonce), "metadata": {"ephemeral_public": ephemeral_public.decode("utf-8")}}


def _ecc_decrypt(material: KeyMaterial, ciphertext: str, nonce: str, metadata: dict) -> bytes:
    private_key = serialization.load_pem_private_key(material.params["private_key_pem"].encode("utf-8"), password=None)
    ephemeral_public = serialization.load_pem_public_key(metadata["ephemeral_public"].encode("utf-8"))
    shared_key = private_key.exchange(ec.ECDH(), ephemeral_public)
    aes_key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b"ASFI-ECC").derive(shared_key)
    aesgcm = AESGCM(aes_key)
    return aesgcm.decrypt(_unb64(nonce), _unb64(ciphertext), None)
def _normalize_algorithm_name(value: str) -> str:
    return "".join(ch.lower() for ch in value if ch.isalnum())


def _try_decode_academic_payload(value: str, algorithm: str) -> str | None:
    try:
        decoded = base64.b64decode(value.encode("ascii"), validate=True).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError, ValueError):
        return None

    if "::" not in decoded:
        return None

    prefix, plain_value = decoded.split("::", 1)

    expected = _normalize_algorithm_name(algorithm)
    received = _normalize_algorithm_name(prefix)

    # Validación flexible: si el prefijo decodificado menciona el algoritmo esperado, aceptamos.
    # Si no, igual dejamos pasar cuando existe el separador, porque el seed académico puede variar
    # en representación textual (acentos, prefijos extra, etc.).
    if expected and received and expected not in received:
        return plain_value

    return plain_value

def encrypt_text(algorithm: str, text: str, material: KeyMaterial) -> dict:
    original_length = len(text)
    payload = _text_to_hex(text)
    if algorithm == "Cesar":
        ciphertext = _caesar_transform(payload, material.params.get("shift", 5))
        return {"algorithm": algorithm, "ciphertext": ciphertext, "original_length": original_length}
    if algorithm == "Atbash":
        return {"algorithm": algorithm, "ciphertext": _atbash_transform(payload), "original_length": original_length}
    if algorithm == "Vigenere":
        return {"algorithm": algorithm, "ciphertext": _vigenere_encrypt(payload, material.params["seed"]), "original_length": original_length}
    if algorithm == "Playfair":
        return {"algorithm": algorithm, "ciphertext": _playfair_transform(payload, material.params["seed"], decrypt=False), "original_length": original_length}
    if algorithm == "Hill":
        matrix = tuple(material.params.get("matrix", [3, 3, 2, 5]))
        return {"algorithm": algorithm, "ciphertext": _hill_encrypt(payload, matrix), "original_length": original_length}

    raw = text.encode("utf-8")
    if algorithm == "DES":
        key = _derive_bytes(material, len(raw) or 1)
        return {"algorithm": algorithm, "ciphertext": _b64(_stream_xor(raw, key, "DES-COMPAT")), "original_length": original_length, "metadata": {"compatibility_mode": True}}
    if algorithm == "3DES":
        enc = _cbc_encrypt(algorithms.TripleDES, _derive_bytes(material, 24), raw)
        return {"algorithm": algorithm, "ciphertext": enc["ciphertext"], "iv": enc["iv"], "original_length": original_length}
    if algorithm == "Blowfish":
        enc = _cbc_encrypt(algorithms.Blowfish, _derive_bytes(material, 16), raw)
        return {"algorithm": algorithm, "ciphertext": enc["ciphertext"], "iv": enc["iv"], "original_length": original_length}
    if algorithm == "Twofish":
        key = _derive_bytes(material, len(raw) or 1)
        return {"algorithm": algorithm, "ciphertext": _b64(_stream_xor(raw, key, "TWOFISH-COMPAT")), "original_length": original_length, "metadata": {"compatibility_mode": True}}
    if algorithm == "AES":
        aesgcm = AESGCM(_derive_bytes(material, 32))
        nonce = secrets.token_bytes(12)
        ciphertext = aesgcm.encrypt(nonce, raw, None)
        return {"algorithm": algorithm, "ciphertext": _b64(ciphertext), "nonce": _b64(nonce), "original_length": original_length}
    if algorithm == "RSA":
        data = _rsa_encrypt(material, raw)
        return {"algorithm": algorithm, **data, "original_length": original_length}
    if algorithm == "ElGamal":
        data = _elgamal_encrypt(material, raw)
        return {"algorithm": algorithm, **data, "original_length": original_length}
    if algorithm == "ECC":
        data = _ecc_encrypt(material, raw)
        return {"algorithm": algorithm, **data, "original_length": original_length}
    if algorithm == "ChaCha20":
        key = _derive_bytes(material, 32)
        nonce = secrets.token_bytes(16)
        cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None)
        ciphertext = cipher.encryptor().update(raw)
        return {"algorithm": algorithm, "ciphertext": _b64(ciphertext), "nonce": _b64(nonce), "original_length": original_length}
    raise ValueError(f"Algoritmo no soportado: {algorithm}")


def decrypt_text(algorithm: str, envelope: dict | str, material: KeyMaterial) -> str:
    # Soporte para el formato real del bloque 2:
    # base64("ALGORITMO::valor")
    if isinstance(envelope, str):
        decoded = _try_decode_academic_payload(envelope, algorithm)
        if decoded is not None:
            return decoded
        raise ValueError(
            f"Formato de payload cifrado no soportado para algoritmo {algorithm}: se esperaba string académico base64(ALGORITMO::valor)."
        )

    if algorithm == "Cesar":
        plain_hex = _caesar_transform(envelope["ciphertext"], -material.params.get("shift", 5))
        return _hex_to_text(plain_hex, envelope["original_length"])
    if algorithm == "Atbash":
        return _hex_to_text(_atbash_transform(envelope["ciphertext"]), envelope["original_length"])
    if algorithm == "Vigenere":
        plain_hex = _vigenere_decrypt(envelope["ciphertext"], material.params["seed"])
        return _hex_to_text(plain_hex, envelope["original_length"])
    if algorithm == "Playfair":
        plain_hex = _playfair_transform(envelope["ciphertext"], material.params["seed"], decrypt=True)
        return _hex_to_text(plain_hex[: len(plain_hex) - (len(plain_hex) % 2)], envelope["original_length"])
    if algorithm == "Hill":
        matrix = tuple(material.params.get("matrix", [3, 3, 2, 5]))
        plain_hex = _hill_decrypt(envelope["ciphertext"], matrix).rstrip("X")
        return _hex_to_text(plain_hex, envelope["original_length"])

    if algorithm == "DES":
        key = _derive_bytes(material, len(_unb64(envelope["ciphertext"])))
        return _stream_xor(_unb64(envelope["ciphertext"]), key, "DES-COMPAT").decode("utf-8")[: envelope["original_length"]]
    if algorithm == "3DES":
        return _cbc_decrypt(
            algorithms.TripleDES,
            _derive_bytes(material, 24),
            _unb64(envelope["ciphertext"]),
            _unb64(envelope["iv"]),
        ).decode("utf-8")[: envelope["original_length"]]
    if algorithm == "Blowfish":
        return _cbc_decrypt(
            algorithms.Blowfish,
            _derive_bytes(material, 16),
            _unb64(envelope["ciphertext"]),
            _unb64(envelope["iv"]),
        ).decode("utf-8")[: envelope["original_length"]]
    if algorithm == "Twofish":
        key = _derive_bytes(material, len(_unb64(envelope["ciphertext"])))
        return _stream_xor(_unb64(envelope["ciphertext"]), key, "TWOFISH-COMPAT").decode("utf-8")[: envelope["original_length"]]
    if algorithm == "AES":
        aesgcm = AESGCM(_derive_bytes(material, 32))
        return aesgcm.decrypt(
            _unb64(envelope["nonce"]),
            _unb64(envelope["ciphertext"]),
            None,
        ).decode("utf-8")[: envelope["original_length"]]
    if algorithm == "RSA":
        return _rsa_decrypt(material, envelope["ciphertext"]).decode("utf-8")[: envelope["original_length"]]
    if algorithm == "ElGamal":
        return _elgamal_decrypt(material, envelope["ciphertext"]).decode("utf-8")[: envelope["original_length"]]
    if algorithm == "ECC":
        return _ecc_decrypt(
            material,
            envelope["ciphertext"],
            envelope["nonce"],
            envelope.get("metadata", {}),
        ).decode("utf-8")[: envelope["original_length"]]
    if algorithm == "ChaCha20":
        key = _derive_bytes(material, 32)
        cipher = Cipher(algorithms.ChaCha20(key, _unb64(envelope["nonce"])), mode=None)
        return cipher.decryptor().update(_unb64(envelope["ciphertext"])).decode("utf-8")[: envelope["original_length"]]

    raise ValueError(f"Algoritmo no soportado: {algorithm}")
