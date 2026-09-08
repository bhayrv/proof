"""
PROOF Protocol — Cryptography

Provides:
- SHA-256 content identity
- Ed25519 key generation
- Ed25519 signing
- Ed25519 signature verification
"""

import hashlib

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


def sha256(data: bytes) -> str:
    """
    Return a content identifier using SHA-256.

    Format:
        sha256:<64 hexadecimal characters>
    """

    digest = hashlib.sha256(data).hexdigest()
    return f"sha256:{digest}"


def generate_private_key() -> Ed25519PrivateKey:
    """Generate a new Ed25519 private key."""
    return Ed25519PrivateKey.generate()


def private_key_bytes(private_key: Ed25519PrivateKey) -> bytes:
    """Export an Ed25519 private key as raw bytes."""
    return private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )


def public_key_bytes(private_key: Ed25519PrivateKey) -> bytes:
    """Export the corresponding public key as raw bytes."""
    return private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def sign(private_key: Ed25519PrivateKey, data: bytes) -> bytes:
    """Sign data with an Ed25519 private key."""
    return private_key.sign(data)


def verify(
    public_key: Ed25519PublicKey,
    signature: bytes,
    data: bytes,
) -> bool:
    """
    Verify an Ed25519 signature.

    Returns:
        True  if valid.
        False if invalid.
    """

    try:
        public_key.verify(signature, data)
        return True
    except Exception:
        return False