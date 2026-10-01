"""Fernet encryption helpers for files stored by the application."""

from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from flask import current_app


class EncryptionConfigurationError(RuntimeError):
    """Raised when the local Fernet key is missing or malformed."""


def get_fernet() -> Fernet:
    """Create a Fernet cipher from the private application configuration."""
    key = current_app.config.get("FERNET_KEY")
    if not key:
        raise EncryptionConfigurationError("FERNET_KEY is not configured.")
    try:
        return Fernet(key.encode())
    except (TypeError, ValueError) as error:
        raise EncryptionConfigurationError("FERNET_KEY is not a valid Fernet key.") from error


def encrypt_file(file_path: Path) -> None:
    """Replace a plaintext file with an encrypted Fernet token atomically."""
    plaintext = file_path.read_bytes()
    ciphertext = get_fernet().encrypt(plaintext)
    temporary_path = file_path.with_suffix(f"{file_path.suffix}.tmp")
    temporary_path.write_bytes(ciphertext)
    temporary_path.replace(file_path)


def decrypt_file(file_path: Path) -> bytes:
    """Return decrypted bytes in memory without creating a plaintext file."""
    try:
        return get_fernet().decrypt(file_path.read_bytes())
    except InvalidToken as error:
        raise ValueError("The file cannot be decrypted with this Fernet key.") from error
