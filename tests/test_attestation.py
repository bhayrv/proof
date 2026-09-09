"""
PROOF Protocol — Attestation Tests

Tests Ed25519 attestation creation, verification, and edge cases.
"""

import pytest

from proof.attestation import (
    Attestation,
    create_attestation,
    signing_payload,
    verify_attestation,
)
from proof.crypto import generate_private_key, load_private_key, public_key_bytes
from proof.evidence import Evidence
from proof.identity import proof_id
from proof.models import Claim, Proof


def _make_proof() -> Proof:
    return Proof(
        claim=Claim("Acme", "raised", "USD 40 million"),
        evidence=[Evidence(type="web", source="https://example.invalid/funding")],
    )


class TestCreateAttestation:
    """Tests for attestation creation."""

    def test_creates_with_generated_key(self):
        proof = _make_proof()
        att, pk_bytes = create_attestation(proof)
        assert att.algorithm == "Ed25519"
        assert att.proof_id == proof_id(proof)
        assert len(pk_bytes) == 32

    def test_creates_with_external_key(self):
        proof = _make_proof()
        key = generate_private_key()
        att, _ = create_attestation(proof, private_key=key)
        expected_pub = public_key_bytes(key).hex()
        assert att.public_key == expected_pub

    def test_created_at_optional(self):
        proof = _make_proof()
        att, _ = create_attestation(proof, created_at="2026-09-08T12:00:00Z")
        assert att.created_at == "2026-09-08T12:00:00Z"

    def test_created_at_default_none(self):
        proof = _make_proof()
        att, _ = create_attestation(proof)
        assert att.created_at is None

    def test_signature_format(self):
        proof = _make_proof()
        att, _ = create_attestation(proof)
        sig_bytes = bytes.fromhex(att.signature)
        assert len(sig_bytes) == 64  # Ed25519 signature size

    def test_public_key_format(self):
        proof = _make_proof()
        att, _ = create_attestation(proof)
        pk_bytes = bytes.fromhex(att.public_key)
        assert len(pk_bytes) == 32  # Ed25519 public key size


class TestVerifyAttestation:
    """Tests for attestation verification."""

    def test_valid_attestation(self):
        proof = _make_proof()
        att, _ = create_attestation(proof)
        assert verify_attestation(proof, att) is True

    def test_modified_claim_fails(self):
        proof = _make_proof()
        att, _ = create_attestation(proof)
        proof.claim.object = "USD 50 million"
        assert verify_attestation(proof, att) is False

    def test_modified_evidence_fails(self):
        proof = _make_proof()
        att, _ = create_attestation(proof)
        proof.evidence = [Evidence(type="web", source="https://other.example.invalid")]
        assert verify_attestation(proof, att) is False

    def test_status_change_does_not_invalidate(self):
        """Changing status must NOT invalidate the attestation."""
        proof = _make_proof()
        att, _ = create_attestation(proof)
        proof.status = "VERIFIED"
        assert verify_attestation(proof, att) is True

    def test_observed_at_change_does_not_invalidate(self):
        """Changing observed_at must NOT invalidate the attestation."""
        proof = _make_proof()
        proof.observed_at = "2026-01-01T00:00:00Z"
        att, _ = create_attestation(proof)
        proof.observed_at = "2026-12-31T23:59:59Z"
        assert verify_attestation(proof, att) is True

    def test_wrong_algorithm(self):
        proof = _make_proof()
        att, _ = create_attestation(proof)
        att.algorithm = "RSA-2048"
        assert verify_attestation(proof, att) is False

    def test_malformed_signature(self):
        proof = _make_proof()
        att, _ = create_attestation(proof)
        att.signature = "deadbeef"  # Too short
        assert verify_attestation(proof, att) is False

    def test_malformed_public_key(self):
        proof = _make_proof()
        att, _ = create_attestation(proof)
        att.public_key = "not_hex_at_all"
        assert verify_attestation(proof, att) is False

    def test_wrong_public_key(self):
        proof = _make_proof()
        att, _ = create_attestation(proof)
        # Use a different key's public key
        other_key = generate_private_key()
        att.public_key = public_key_bytes(other_key).hex()
        assert verify_attestation(proof, att) is False

    def test_wrong_proof_id(self):
        proof = _make_proof()
        att, _ = create_attestation(proof)
        att.proof_id = "sha256:" + "0" * 64
        assert verify_attestation(proof, att) is False


class TestSigningPayload:
    """Tests for the signing payload."""

    def test_signing_payload_is_bytes(self):
        proof = _make_proof()
        payload = signing_payload(proof)
        assert isinstance(payload, bytes)

    def test_signing_payload_deterministic(self):
        a = _make_proof()
        b = _make_proof()
        assert signing_payload(a) == signing_payload(b)

    def test_signing_payload_independent_of_status(self):
        a = _make_proof()
        a.status = "OBSERVED"
        b = _make_proof()
        b.status = "VERIFIED"
        assert signing_payload(a) == signing_payload(b)


class TestAttestationSerialization:
    """Tests for attestation to_dict."""

    def test_to_dict_required_fields(self):
        att = Attestation(
            proof_id="sha256:" + "a" * 64,
            algorithm="Ed25519",
            public_key="b" * 64,
            signature="c" * 128,
        )
        d = att.to_dict()
        assert d["proof_id"] == "sha256:" + "a" * 64
        assert d["algorithm"] == "Ed25519"
        assert "created_at" not in d

    def test_to_dict_with_created_at(self):
        att = Attestation(
            proof_id="sha256:" + "a" * 64,
            algorithm="Ed25519",
            public_key="b" * 64,
            signature="c" * 128,
            created_at="2026-09-08T12:00:00Z",
        )
        d = att.to_dict()
        assert d["created_at"] == "2026-09-08T12:00:00Z"


class TestLoadPrivateKey:
    """Tests for loading private keys from bytes."""

    def test_round_trip(self):
        from proof.crypto import private_key_bytes

        key = generate_private_key()
        raw = private_key_bytes(key)
        loaded = load_private_key(raw)
        assert private_key_bytes(loaded) == raw

    def test_wrong_length_raises(self):
        with pytest.raises(ValueError, match="32 bytes"):
            load_private_key(b"too_short")
