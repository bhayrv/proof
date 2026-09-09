"""
PROOF Protocol — Verification

Provides structured verification of PROOF records.  Verification
distinguishes cryptographic validity from factual truth.

A verification result answers:
    - Is the identity valid?
    - Do attestation signatures verify?
    - Is evidence present?
    - What is the lifecycle status?
    - Were there any errors?

See spec/PROOF.md §8 for the normative specification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .attestation import Attestation, verify_attestation
from .identity import proof_id
from .models import Proof


@dataclass
class VerificationResult:
    """Structured result of verifying a PROOF record.

    This is NOT a simplistic true/false answer.  Each dimension of
    validity is reported independently so that consumers can apply
    their own policies.
    """

    identity_valid: bool = False
    signature_valid: bool = False
    evidence_present: bool = False
    lifecycle_status: str = ""
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """Return ``True`` if there are no errors."""
        return len(self.errors) == 0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-compatible dictionary."""
        return {
            "identity_valid": self.identity_valid,
            "signature_valid": self.signature_valid,
            "evidence_present": self.evidence_present,
            "lifecycle_status": self.lifecycle_status,
            "errors": list(self.errors),
        }


def verify_proof(
    proof: Proof,
    attestations: list[Attestation] | None = None,
) -> VerificationResult:
    """Verify a PROOF record and return a structured result.

    Parameters
    ----------
    proof
        The PROOF record to verify.
    attestations
        Attestations to verify against the record.  If ``None``,
        no signature verification is performed (``signature_valid``
        defaults to ``False``).

    Returns
    -------
    VerificationResult
        A structured result with independent validity dimensions.
    """
    result = VerificationResult()
    result.lifecycle_status = proof.status

    # 1. Identity check
    if proof.id is not None:
        computed = proof_id(proof)
        if proof.id == computed:
            result.identity_valid = True
        else:
            result.errors.append(
                f"Identity mismatch: expected {computed}, got {proof.id}"
            )
    else:
        # No id set — compute it for reference but don't flag error
        result.identity_valid = True

    # 2. Evidence check
    result.evidence_present = len(proof.evidence) > 0
    if not result.evidence_present:
        result.errors.append("No evidence records present")

    # 3. Attestation/signature check
    if attestations:
        all_valid = True
        for i, att in enumerate(attestations):
            if not verify_attestation(proof, att):
                all_valid = False
                result.errors.append(
                    f"Attestation {i} failed verification"
                )
        result.signature_valid = all_valid
    else:
        # No attestations provided — not an error, just unsigned
        result.signature_valid = False
        if attestations is not None and len(attestations) == 0:
            result.errors.append("Empty attestation list provided")

    return result
