"""
PROOF Protocol — Content Identity

A PROOF identity is derived from the canonical representation of
the record's immutable content — protocol version, claim, and evidence.

Mutable fields (status, observed_at, attestations, id) are excluded.

See spec/PROOF.md §4 for the normative specification.
"""

from __future__ import annotations

from .canonical import canonicalize
from .crypto import sha256
from .models import Proof


def identity_payload(proof: Proof) -> dict:
    """Return the exact content used to calculate a PROOF identity.

    This is the immutable subset:

    * ``proof`` — protocol version
    * ``claim`` — the claim
    * ``evidence`` — evidence records

    The ``id``, ``status``, ``observed_at``, and ``attestations``
    fields are deliberately excluded.
    """
    return proof.content_dict()


def proof_id(proof: Proof) -> str:
    """Generate the deterministic content identity of a PROOF record.

    Returns
    -------
    str
        Identity string in the format ``sha256:<64 hex chars>``.
    """
    payload = identity_payload(proof)
    data = canonicalize(payload)
    return sha256(data)