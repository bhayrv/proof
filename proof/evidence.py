"""
PROOF Protocol — Evidence Model

Evidence describes the material supporting a claim.

PROOF does not decide whether evidence is true.
It records what evidence exists and how it can be identified.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Evidence:
    """A piece of material associated with a PROOF claim.

    Required fields:
        type   -- category of evidence (e.g. "web", "document", "api",
                  "dataset", "proof")
        source -- URI, identifier, or location of the evidence

    Optional fields:
        title        -- human-readable title
        content_hash -- content hash for integrity ("sha256:<hex>")
        observed_at  -- ISO 8601 timestamp of observation
        metadata     -- additional structured metadata
    """

    type: str
    source: str
    title: str | None = None
    content_hash: str | None = None
    observed_at: str | None = None
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict:
        """Convert evidence into a JSON-compatible dictionary.

        Only non-None optional fields are included.  The field order
        matches the protocol specification.
        """
        result: dict[str, Any] = {
            "type": self.type,
            "source": self.source,
        }

        if self.title is not None:
            result["title"] = self.title

        if self.content_hash is not None:
            result["content_hash"] = self.content_hash

        if self.observed_at is not None:
            result["observed_at"] = self.observed_at

        if self.metadata is not None:
            result["metadata"] = self.metadata

        return result