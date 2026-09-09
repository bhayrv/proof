"""
PROOF Protocol — Identity Tests

Tests the immutable content identity model defined in spec/PROOF.md §4.
"""

from proof.evidence import Evidence
from proof.identity import identity_payload, proof_id
from proof.models import Claim, Proof, PROTOCOL_VERSION


def _make_proof(**kwargs) -> Proof:
    """Helper to create a test PROOF record with overrides."""
    defaults = {
        "claim": Claim(subject="Acme", predicate="raised", object="USD 40 million"),
        "evidence": [Evidence(type="web", source="https://example.invalid/funding")],
        "observed_at": "2026-09-08T00:00:00Z",
        "status": "OBSERVED",
    }
    defaults.update(kwargs)
    return Proof(**defaults)


class TestIdentityPayload:
    """Tests for the identity payload construction."""

    def test_includes_protocol_version(self):
        proof = _make_proof()
        payload = identity_payload(proof)
        assert payload["proof"] == PROTOCOL_VERSION

    def test_includes_claim(self):
        proof = _make_proof()
        payload = identity_payload(proof)
        assert payload["claim"]["subject"] == "Acme"
        assert payload["claim"]["predicate"] == "raised"
        assert payload["claim"]["object"] == "USD 40 million"

    def test_includes_evidence(self):
        proof = _make_proof()
        payload = identity_payload(proof)
        assert len(payload["evidence"]) == 1
        assert payload["evidence"][0]["type"] == "web"

    def test_excludes_id(self):
        proof = _make_proof()
        proof.id = "sha256:abcd1234" * 8  # fake ID
        payload = identity_payload(proof)
        assert "id" not in payload

    def test_excludes_status(self):
        proof = _make_proof(status="VERIFIED")
        payload = identity_payload(proof)
        assert "status" not in payload

    def test_excludes_observed_at(self):
        proof = _make_proof(observed_at="2026-09-08T00:00:00Z")
        payload = identity_payload(proof)
        assert "observed_at" not in payload

    def test_excludes_attestations(self):
        proof = _make_proof()
        proof.attestations = [{"proof_id": "sha256:fake"}]
        payload = identity_payload(proof)
        assert "attestations" not in payload


class TestProofId:
    """Tests for the proof_id function."""

    def test_identity_format(self):
        proof = _make_proof()
        pid = proof_id(proof)
        assert pid.startswith("sha256:")
        assert len(pid) == 71  # "sha256:" + 64 hex chars

    def test_deterministic(self):
        a = _make_proof()
        b = _make_proof()
        assert proof_id(a) == proof_id(b)

    def test_different_claim_different_identity(self):
        a = _make_proof(claim=Claim("A", "did", "X"))
        b = _make_proof(claim=Claim("B", "did", "X"))
        assert proof_id(a) != proof_id(b)

    def test_different_evidence_different_identity(self):
        a = _make_proof(evidence=[Evidence(type="web", source="https://a.example.invalid")])
        b = _make_proof(evidence=[Evidence(type="web", source="https://b.example.invalid")])
        assert proof_id(a) != proof_id(b)

    def test_status_does_not_affect_identity(self):
        """Changing status must NOT change identity."""
        a = _make_proof(status="OBSERVED")
        b = _make_proof(status="VERIFIED")
        assert proof_id(a) == proof_id(b)

    def test_observed_at_does_not_affect_identity(self):
        """Changing observed_at must NOT change identity."""
        a = _make_proof(observed_at="2026-01-01T00:00:00Z")
        b = _make_proof(observed_at="2026-12-31T23:59:59Z")
        assert proof_id(a) == proof_id(b)

    def test_attestations_do_not_affect_identity(self):
        """Adding attestations must NOT change identity."""
        a = _make_proof()
        b = _make_proof()
        b.attestations = [{"proof_id": "sha256:fake", "algorithm": "Ed25519"}]
        assert proof_id(a) == proof_id(b)

    def test_empty_evidence_different_from_evidence(self):
        a = _make_proof(evidence=[])
        b = _make_proof(evidence=[Evidence(type="web", source="https://example.invalid")])
        assert proof_id(a) != proof_id(b)

    def test_structured_object_value(self):
        """Structured JSON objects as claim values produce valid identities."""
        proof = _make_proof(
            claim=Claim("Acme", "reported", {"revenue": 1000000, "currency": "USD"})
        )
        pid = proof_id(proof)
        assert pid.startswith("sha256:")
