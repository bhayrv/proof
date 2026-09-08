"""
PROOF Protocol — Content Identity

A PROOF identity is derived from the canonical content of the
record, excluding the identity field itself.

This makes the identity self-consistent:
the record can carry its own ID without changing that ID.
"""

from .canonical import canonicalize
from .crypto import sha256
from .models import Proof


def identity_payload(proof: Proof) -> dict:
    """
    Return the exact content used to calculate a PROOF identity.

    The `id` field is deliberately excluded because the identity
    cannot be included in the data used to calculate itself.
    """

    data = proof.to_dict()
    data.pop("id", None)
    return data


def proof_id(proof: Proof) -> str:
    """
    Generate the deterministic content identity of a PROOF object.
    """

    data = canonicalize(identity_payload(proof))
    return sha256(data)