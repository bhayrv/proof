"""
PROOF Protocol — Cryptography

Provides:
    - SHA-256 content identity
    - Ed25519 key generation
    - Ed25519 signing
    - Ed25519 signature verification
    - Key import/export helpers
"""

from __future__ import annotations

import hashlib

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


def sha256(data: bytes) -> str:
    """Return a content identifier using SHA-256.

    Format::

        sha256:<64 lowercase hexadecimal characters>
    """
    digest = hashlib.sha256(data).hexdigest()
    return f"sha256:{digest}"


def generate_private_key() -> Ed25519PrivateKey:
    """Generate a new Ed25519 private key.

    This is a convenience helper for testing and examples.
    Production systems should use externally managed keys.
    """
    return Ed25519PrivateKey.generate()


def load_private_key(raw_bytes: bytes) -> Ed25519PrivateKey:
    """Load an Ed25519 private key from 32 raw bytes.

    Parameters
    ----------
    raw_bytes
        Exactly 32 bytes of raw Ed25519 private key material.

    Returns
    -------
    Ed25519PrivateKey
        The reconstructed private key.

    Raises
    ------
    ValueError
        If *raw_bytes* is not exactly 32 bytes.
    """
    if len(raw_bytes) != 32:
        raise ValueError(
            f"Ed25519 private key must be 32 bytes, got {len(raw_bytes)}"
        )
    return Ed25519PrivateKey.from_private_bytes(raw_bytes)


def private_key_bytes(private_key: Ed25519PrivateKey) -> bytes:
    """Export an Ed25519 private key as raw bytes (32 bytes)."""
    return private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )


def public_key_bytes(private_key: Ed25519PrivateKey) -> bytes:
    """Export the corresponding public key as raw bytes (32 bytes)."""
    return private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def sign(private_key: Ed25519PrivateKey, data: bytes) -> bytes:
    """Sign *data* with an Ed25519 private key.

    Returns
    -------
    bytes
        The 64-byte Ed25519 signature.
    """
    return private_key.sign(data)


def verify(
    public_key: Ed25519PublicKey,
    signature: bytes,
    data: bytes,
) -> bool:
    """Verify an Ed25519 signature.

    Returns
    -------
    bool
        ``True`` if the signature is valid, ``False`` otherwise.
    """
    try:
        public_key.verify(signature, data)
        return True
    except Exception:
        return False