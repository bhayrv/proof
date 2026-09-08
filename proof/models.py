"""
PROOF Protocol — Core Data Model

Defines the core structure of a PROOF claim and its evidence.
"""

from dataclasses import dataclass, field
from typing import Any

from .evidence import Evidence


@dataclass
class Claim:
    """
    A machine-readable statement about something.

    Example:
        subject   = "Acme"
        predicate = "raised"
        object    = "USD 40 million"
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
    """
    The core PROOF record.

    The `id` field is assigned after the record's content has been
    constructed. The ID itself is not part of the content used to
    calculate the identity.
    """

    claim: Claim
    evidence: list[Evidence] = field(default_factory=list)
    attestations: list[dict] = field(default_factory=list)
    observed_at: str | None = None
    status: str = "OBSERVED"
    id: str | None = None

    def to_dict(self) -> dict:
        """Convert the complete PROOF record to a dictionary."""

        result = {
            "proof": "0.1",
            "claim": self.claim.to_dict(),
            "evidence": [
                item.to_dict() for item in self.evidence
            ],
            "attestations": self.attestations,
            "observed_at": self.observed_at,
            "status": self.status,
        }

        if self.id is not None:
            result["id"] = self.id

        return result