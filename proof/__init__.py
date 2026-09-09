"""
PROOF Protocol — Python Reference Implementation

Public API
----------

Data model::

    from proof import Claim, Evidence, Proof

Identity::

    from proof import proof_id

Attestations::

    from proof import Attestation, create_attestation, verify_attestation

Verification::

    from proof import VerificationResult, verify_proof

Lifecycle::

    from proof import Status

Graph::

    from proof import ProofRelation, ProofGraph, Relation

Canonicalization::

    from proof import canonicalize
"""

from .attestation import Attestation, create_attestation, verify_attestation
from .canonical import canonicalize
from .evidence import Evidence
from .graph import ProofGraph, ProofRelation, Relation
from .identity import proof_id
from .lifecycle import Status
from .models import Claim, Proof
from .verify import VerificationResult, verify_proof

__all__ = [
    # Data model
    "Claim",
    "Evidence",
    "Proof",
    # Identity
    "proof_id",
    # Attestations
    "Attestation",
    "create_attestation",
    "verify_attestation",
    # Verification
    "VerificationResult",
    "verify_proof",
    # Lifecycle
    "Status",
    # Graph
    "ProofRelation",
    "ProofGraph",
    "Relation",
    # Canonicalization
    "canonicalize",
]
