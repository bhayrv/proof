"""
PROOF Protocol — Evidence Model

Evidence describes the material supporting a claim.

PROOF does not decide whether evidence is true.
It records what evidence exists and how it can be identified.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class Evidence:
    """
    A piece of material associated with a PROOF claim.

    Examples:
    - A URL
    - A document
    - A database record
    - An API response
    - A scientific dataset
    - Another PROOF claim
    """

    type: str
    source: str
    title: str | None = None
    content_hash: str | None = None
    observed_at: str | None = None
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict:
        """Convert evidence into a JSON-compatible dictionary."""

        result = {
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