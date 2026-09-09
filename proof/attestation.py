"""
PROOF Protocol — Attestations

Cryptographic attestations bind an identity to a specific PROOF record.

A valid signature proves:
    1. The signer controlled the corresponding private key.
    2. The signed PROOF bytes have not changed.

A valid signature does NOT prove that the claim itself is true.

Signing payload (PROOF 0.2):
    The canonical bytes of the *identity payload* — the immutable
    subset of the record (protocol version, claim, evidence).  This
    means signatures remain valid across lifecycle/status changes and
    additional attestations.

See spec/PROOF.md §5 for the normative specification.
"""

from __future__ import annotations

from dataclasses import dataclass

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from .canonical import canonicalize
from .crypto import (
    generate_private_key,
    private_key_bytes,
    public_key_bytes,
    sign,
    verify,
)
from .identity import identity_payload, proof_id
from .models import Proof


@dataclass
class Attestation:
    """A cryptographic attestation for a PROOF record.

    Fields
    ------
    proof_id : str
        The PROOF identity being attested.
    algorithm : str
        Signing algorithm identifier (currently only ``"Ed25519"``).
    public_key : str
        Hex-encoded raw public key bytes (32 bytes for Ed25519).
    signature : str
        Hex-encoded raw signature bytes (64 bytes for Ed25519).
    created_at : str or None
        ISO 8601 timestamp of attestation creation (optional).
    """

    proof_id: str
    algorithm: str
    public_key: str
    signature: str
    created_at: str | None = None

    def to_dict(self) -> dict:
        """Convert the attestation to a JSON-compatible dictionary."""
        result: dict = {
            "proof_id": self.proof_id,
            "algorithm": self.algorithm,
            "public_key": self.public_key,
            "signature": self.signature,
        }
        if self.created_at is not None:
            result["created_at"] = self.created_at
        return result


def signing_payload(proof: Proof) -> bytes:
    """Return the canonical bytes that are signed for an attestation.

    This is the canonical serialization of the identity payload —
    the same bytes used to compute the PROOF identity.
    """
    return canonicalize(identity_payload(proof))


def create_attestation(
    proof: Proof,
    private_key: Ed25519PrivateKey | None = None,
    created_at: str | None = None,
) -> tuple[Attestation, bytes]:
    """Create an Ed25519 attestation for a PROOF record.

    Parameters
    ----------
    proof
        The PROOF record to attest.
    private_key
        An externally managed Ed25519 private key.  If ``None``, a new
        key is generated (convenience for tests/examples).
    created_at
        Optional ISO 8601 timestamp for the attestation.

    Returns
    -------
    tuple[Attestation, bytes]
        ``(attestation, raw_private_key_bytes)``

        The private key bytes are returned so the caller can securely
        store them.  They should not be persisted unnecessarily.
    """
    if private_key is None:
        private_key = generate_private_key()

    data = signing_payload(proof)
    sig = sign(private_key, data)

    attestation = Attestation(
        proof_id=proof_id(proof),
        algorithm="Ed25519",
        public_key=public_key_bytes(private_key).hex(),
        signature=sig.hex(),
        created_at=created_at,
    )

    return attestation, private_key_bytes(private_key)


def verify_attestation(
    proof: Proof,
    attestation: Attestation,
) -> bool:
    """Verify an attestation against a PROOF record.

    Verification checks:

    1. The algorithm is supported (``Ed25519``).
    2. The attestation references the correct PROOF identity.
    3. The Ed25519 signature is valid for the canonical identity
       payload bytes.

    Returns
    -------
    bool
        ``True`` if all checks pass, ``False`` otherwise.

    Notes
    -----
    The private key is never required for verification.
    """
    if attestation.algorithm != "Ed25519":
        return False

    # Check identity binding.
    current_id = proof_id(proof)
    if attestation.proof_id != current_id:
        return False

    try:
        pub_key = Ed25519PublicKey.from_public_bytes(
            bytes.fromhex(attestation.public_key)
        )
        sig = bytes.fromhex(attestation.signature)
        data = signing_payload(proof)
        return verify(pub_key, sig, data)
    except (ValueError, TypeError):
        return False