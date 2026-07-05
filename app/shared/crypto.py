"""Field-level encryption helpers for sensitive PII (bank account numbers)."""

import base64
import hashlib

from cryptography.fernet import Fernet

from app.core.config import settings


def _fernet() -> Fernet:
    digest = hashlib.sha256(settings.secret_key.encode()).digest()
    key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


def encrypt_value(plaintext: str) -> bytes:
    return _fernet().encrypt(plaintext.encode())


def decrypt_value(ciphertext: bytes) -> str:
    return _fernet().decrypt(ciphertext).decode()


def mask_account_number(account_number: str) -> str:
    digits = account_number.strip()
    if len(digits) <= 4:
        return "X" * max(len(digits), 4)
    return f"{'X' * (len(digits) - 4)}{digits[-4:]}"
