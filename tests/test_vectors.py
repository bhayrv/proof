"""
PROOF Protocol — Test Vector Validation

Validates the implementation against the deterministic conformance
vectors in spec/test-vectors/.

These tests ensure that any independent implementation following the
specification will produce identical results.
"""

import json
import pathlib

import pytest

from proof.canonical import canonicalize
from proof.crypto import sha256

VECTORS_DIR = pathlib.Path(__file__).resolve().parent.parent / "spec" / "test-vectors"


class TestCanonicalVectors:
    """Validate canonical serialization against test vectors."""

    @pytest.fixture
    def vectors(self):
        with open(VECTORS_DIR / "canonicalization.json", encoding="utf-8") as f:
            return json.load(f)["vectors"]

    def test_all_canonical_vectors(self, vectors):
        for vec in vectors:
            canonical_bytes = canonicalize(vec["input"])
            expected_hex = vec["canonical_hex"]
            assert canonical_bytes.hex() == expected_hex, (
                f"Vector '{vec['name']}': canonical hex mismatch\n"
                f"  expected: {expected_hex}\n"
                f"  got:      {canonical_bytes.hex()}"
            )

    def test_all_canonical_sha256(self, vectors):
        for vec in vectors:
            canonical_bytes = canonicalize(vec["input"])
            computed_hash = sha256(canonical_bytes)
            assert computed_hash == vec["sha256"], (
                f"Vector '{vec['name']}': SHA-256 mismatch\n"
                f"  expected: {vec['sha256']}\n"
                f"  got:      {computed_hash}"
            )


class TestIdentityVectors:
    """Validate identity computation against test vectors."""

    @pytest.fixture
    def vectors(self):
        with open(VECTORS_DIR / "identity.json", encoding="utf-8") as f:
            return json.load(f)["vectors"]

    def test_all_identity_vectors(self, vectors):
        for vec in vectors:
            canonical_bytes = canonicalize(vec["identity_payload"])
            assert canonical_bytes.hex() == vec["canonical_hex"], (
                f"Vector '{vec['name']}': canonical hex mismatch"
            )
            computed_id = sha256(canonical_bytes)
            assert computed_id == vec["expected_identity"], (
                f"Vector '{vec['name']}': identity mismatch\n"
                f"  expected: {vec['expected_identity']}\n"
                f"  got:      {computed_id}"
            )


class TestAttestationVectors:
    """Validate attestation signing/verification against test vectors."""

    @pytest.fixture
    def vectors(self):
        with open(VECTORS_DIR / "attestation.json", encoding="utf-8") as f:
            return json.load(f)["vectors"]

    def test_valid_attestation_vector(self, vectors):
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PublicKey,
        )

        vec = vectors[0]
        assert vec["name"] == "valid_attestation"

        # Verify the signing payload matches
        canonical_bytes = canonicalize(vec["identity_payload"])
        assert canonical_bytes.hex() == vec["signing_payload_hex"]

        # Verify the identity matches
        computed_id = sha256(canonical_bytes)
        assert computed_id == vec["proof_id"]

        # Verify the signature
        pub_key = Ed25519PublicKey.from_public_bytes(
            bytes.fromhex(vec["public_key_hex"])
        )
        signature = bytes.fromhex(vec["signature_hex"])
        # Should not raise
        pub_key.verify(signature, canonical_bytes)

    def test_tampered_attestation_vector(self, vectors):
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PublicKey,
        )
        from cryptography.exceptions import InvalidSignature

        vec = vectors[1]
        assert vec["name"] == "tampered_claim"

        canonical_bytes = canonicalize(vec["identity_payload"])
        pub_key = Ed25519PublicKey.from_public_bytes(
            bytes.fromhex(vec["public_key_hex"])
        )
        signature = bytes.fromhex(vec["signature_hex"])

        with pytest.raises(InvalidSignature):
            pub_key.verify(signature, canonical_bytes)
