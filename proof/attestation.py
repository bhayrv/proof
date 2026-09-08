"""
PROOF Protocol — Attestations

Cryptographic attestations bind an identity to a specific PROOF object.

A valid signature proves:
1. The signer controlled the corresponding private key.
2. The signed PROOF bytes have not changed.

A valid signature does NOT prove that the claim itself is true.
"""

from dataclasses import dataclass

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .canonical import canonicalize
from .crypto import (
    generate_private_key,
    private_key_bytes,
    public_key_bytes,
    sign,
    verify,
)
from .identity import proof_id
from .models import Proof


@dataclass
class Attestation:
    """A cryptographic attestation for a PROOF object."""

    proof_id: str
    algorithm: str
    public_key: str
    signature: str

    def to_dict(self) -> dict:
        """Convert the attestation to a JSON-compatible dictionary."""

        return {
            "proof_id": self.proof_id,
            "algorithm": self.algorithm,
            "public_key": self.public_key,
            "signature": self.signature,
        }


def create_attestation(
    proof: Proof,
) -> tuple[Attestation, bytes]:
    """
    Create an Ed25519 attestation for a PROOF object.

    Returns:
        (attestation, private_key_bytes)

    The private key is returned only so the caller can securely store it.
    """

    private_key = generate_private_key()

    data = canonicalize(proof.to_dict())
    signature = sign(private_key, data)

    attestation = Attestation(
        proof_id=proof_id(proof),
        algorithm="Ed25519",
        public_key=public_key_bytes(private_key).hex(),
        signature=signature.hex(),
    )

    return attestation, private_key_bytes(private_key)


def verify_attestation(
    proof: Proof,
    attestation: Attestation,
) -> bool:
    """
    Independently verify an attestation against a PROOF object.

    Verification checks:

    1. The attestation references the correct PROOF identity.
    2. The Ed25519 signature is valid for the canonical PROOF bytes.

    The private key is never required.
    """

    if attestation.algorithm != "Ed25519":
        return False

    current_proof_id = proof_id(proof)

    if attestation.proof_id != current_proof_id:
        return False

    try:
        public_key = Ed25519PublicKey.from_public_bytes(
            bytes.fromhex(attestation.public_key)
        )

        signature = bytes.fromhex(attestation.signature)

        data = canonicalize(proof.to_dict())

        return verify(
            public_key,
            signature,
            data,
        )

    except (ValueError, TypeError):
        return False