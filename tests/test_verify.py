"""
PROOF Protocol — Verification Tests

Tests the structured verification API defined in spec/PROOF.md §8.
"""

from proof.attestation import Attestation, create_attestation
from proof.evidence import Evidence
from proof.identity import proof_id
from proof.models import Claim, Proof
from proof.verify import VerificationResult, verify_proof


def _make_proof() -> Proof:
    return Proof(
        claim=Claim("Acme", "raised", "USD 40 million"),
        evidence=[Evidence(type="web", source="https://example.invalid/funding")],
        observed_at="2026-09-08T00:00:00Z",
    )


class TestVerificationResult:
    """Tests for the VerificationResult dataclass."""

    def test_default_values(self):
        r = VerificationResult()
        assert r.identity_valid is False
        assert r.signature_valid is False
        assert r.evidence_present is False
        assert r.lifecycle_status == ""
        assert r.errors == []

    def test_ok_when_no_errors(self):
        r = VerificationResult()
        assert r.ok is True

    def test_not_ok_when_errors(self):
        r = VerificationResult(errors=["something went wrong"])
        assert r.ok is False

    def test_to_dict(self):
        r = VerificationResult(
            identity_valid=True,
            signature_valid=True,
            evidence_present=True,
            lifecycle_status="OBSERVED",
        )
        d = r.to_dict()
        assert d["identity_valid"] is True
        assert d["errors"] == []


class TestVerifyProof:
    """Tests for the verify_proof function."""

    def test_valid_proof_with_attestation(self):
        proof = _make_proof()
        proof.id = proof_id(proof)
        att, _ = create_attestation(proof)
        result = verify_proof(proof, attestations=[att])

        assert result.identity_valid is True
        assert result.signature_valid is True
        assert result.evidence_present is True
        assert result.lifecycle_status == "OBSERVED"
        assert result.ok is True

    def test_identity_mismatch(self):
        proof = _make_proof()
        proof.id = "sha256:" + "0" * 64  # wrong identity
        result = verify_proof(proof)
        assert result.identity_valid is False
        assert any("mismatch" in e.lower() for e in result.errors)

    def test_no_id_set(self):
        proof = _make_proof()
        result = verify_proof(proof)
        assert result.identity_valid is True  # no id to mismatch

    def test_no_evidence(self):
        proof = Proof(
            claim=Claim("Acme", "raised", "USD 40 million"),
            evidence=[],
        )
        result = verify_proof(proof)
        assert result.evidence_present is False
        assert any("evidence" in e.lower() for e in result.errors)

    def test_no_attestations(self):
        proof = _make_proof()
        result = verify_proof(proof)
        assert result.signature_valid is False

    def test_invalid_attestation(self):
        proof = _make_proof()
        proof.id = proof_id(proof)
        # Create an attestation then tamper with the proof
        att, _ = create_attestation(proof)
        proof.claim.object = "TAMPERED"
        result = verify_proof(proof, attestations=[att])
        assert result.signature_valid is False
        assert any("failed" in e.lower() for e in result.errors)

    def test_lifecycle_status_reported(self):
        proof = _make_proof()
        proof.status = "CONTESTED"
        result = verify_proof(proof)
        assert result.lifecycle_status == "CONTESTED"

    def test_empty_attestation_list(self):
        proof = _make_proof()
        result = verify_proof(proof, attestations=[])
        assert result.signature_valid is False
        assert any("empty" in e.lower() for e in result.errors)
