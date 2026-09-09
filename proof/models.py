"""
PROOF Protocol — Core Data Model

Defines the core structures of a PROOF 0.2 record: ``Claim`` and
``Proof``.

Key design decision (PROOF 0.2):
    The *identity* is derived only from immutable content — protocol
    version, claim, and evidence.  Mutable fields (status, observed_at,
    attestations) are excluded so that lifecycle changes do not
    invalidate existing attestations.

See spec/PROOF.md §3 for the normative specification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .evidence import Evidence
from .lifecycle import Status

# Protocol version constant.
PROTOCOL_VERSION: str = "0.2"


@dataclass
class Claim:
    """A machine-readable statement about something.

    A claim has three components:

    * ``subject``   — the entity the claim is about
    * ``predicate`` — the relationship or action being asserted
    * ``object``    — the value of the assertion (any JSON-compatible value)

    Example::

        Claim(subject="Acme", predicate="raised", object="USD 40 million")
    """

    subject: str
    predicate: str
    object: Any

    def to_dict(self) -> dict:
        """Convert the claim into a JSON-compatible dictionary."""
        return {
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.object,
        }


@dataclass
class Proof:
    """The core PROOF 0.2 record.

    The ``id`` field is assigned *after* the record's content has been
    constructed.  It is not part of the content used to calculate the
    identity (see :func:`proof.identity.proof_id`).

    The ``status`` and ``observed_at`` fields are mutable lifecycle
    metadata — they are also excluded from identity computation.
    """

    claim: Claim
    evidence: list[Evidence] = field(default_factory=list)
    attestations: list[dict] = field(default_factory=list)
    observed_at: str | None = None
    status: str = Status.OBSERVED.value
    id: str | None = None

    # ------------------------------------------------------------------ #
    #  Serialization
    # ------------------------------------------------------------------ #

    def content_dict(self) -> dict:
        """Return only the immutable, identity-participating fields.

        This is the exact payload used for identity computation and
        attestation signing.  It includes:

        * ``proof`` — protocol version
        * ``claim`` — the claim
        * ``evidence`` — evidence records

        It excludes: ``id``, ``status``, ``observed_at``, ``attestations``.
        """
        return {
            "proof": PROTOCOL_VERSION,
            "claim": self.claim.to_dict(),
            "evidence": [e.to_dict() for e in self.evidence],
        }

    def to_dict(self) -> dict:
        """Convert the complete PROOF record to a dictionary.

        The returned dictionary includes all fields — both immutable
        content and mutable metadata.
        """
        result: dict[str, Any] = {
            "proof": PROTOCOL_VERSION,
            "claim": self.claim.to_dict(),
            "evidence": [e.to_dict() for e in self.evidence],
            "attestations": self.attestations,
            "observed_at": self.observed_at,
            "status": self.status,
        }

        if self.id is not None:
            result["id"] = self.id

        return result