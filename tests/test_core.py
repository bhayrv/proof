"""
PROOF Protocol — Core Tests

These tests protect the fundamental invariants of PROOF 0.1.
"""

from proof.attestation import create_attestation, verify_attestation
from proof.evidence import Evidence
from proof.identity import proof_id
from proof.models import Claim, Proof


def make_proof(amount: str = "USD 40 million") -> Proof:
    """Create a deterministic test PROOF record."""

    claim = Claim(
        subject="Acme",
        predicate="raised",
        object=amount,
    )

    evidence = Evidence(
        type="web",
        source="https://example.com/acme-funding",
        title="Acme funding announcement",
        observed_at="2026-09-08T00:00:00Z",
    )

    return Proof(
        claim=claim,
        evidence=[evidence],
        observed_at="2026-09-08T00:00:00Z",
    )


def test_same_content_has_same_identity():
    """Identical PROOF content must produce identical identities."""

    proof_a = make_proof()
    proof_b = make_proof()

    assert proof_id(proof_a) == proof_id(proof_b)


def test_different_content_has_different_identity():
    """Changing PROOF content must change its identity."""

    proof_a = make_proof("USD 40 million")
    proof_b = make_proof("USD 50 million")

    assert proof_id(proof_a) != proof_id(proof_b)


def test_identity_is_self_consistent():
    """Attaching an identity must not change that identity."""

    proof = make_proof()

    identity = proof_id(proof)
    proof.id = identity

    assert proof_id(proof) == identity


def test_valid_signature_verifies():
    """An authentic signature must verify successfully."""

    proof = make_proof()

    attestation, _ = create_attestation(proof)

    assert verify_attestation(proof, attestation) is True


def test_modified_proof_fails_verification():
    """Changing signed content must invalidate the signature."""

    proof = make_proof()

    attestation, _ = create_attestation(proof)

    proof.claim.object = "USD 50 million"

    assert verify_attestation(proof, attestation) is False