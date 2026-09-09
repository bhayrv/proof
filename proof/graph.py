"""
PROOF Protocol — Graph Relationships

Defines typed relationships between PROOF records and provides a
simple in-memory graph for querying them.

Relationship types:
    supports     — source provides supporting evidence for target
    contradicts  — source presents evidence contradicting target
    supersedes   — source is an updated version of target
    derived_from — source was derived from or based on target
    corroborates — source independently confirms target

See spec/PROOF.md §7 for the normative specification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Relation(str, Enum):
    """PROOF graph relationship types."""

    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    SUPERSEDES = "supersedes"
    DERIVED_FROM = "derived_from"
    CORROBORATES = "corroborates"


@dataclass
class ProofRelation:
    """A typed relationship between two PROOF records.

    Parameters
    ----------
    source_id
        PROOF identity of the source record.
    target_id
        PROOF identity of the target record.
    relation
        The relationship type.
    metadata
        Optional additional relationship metadata.
    """

    source_id: str
    target_id: str
    relation: str
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict:
        """Convert the relationship to a JSON-compatible dictionary."""
        result: dict[str, Any] = {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation": self.relation,
        }
        if self.metadata is not None:
            result["metadata"] = self.metadata
        return result


class ProofGraph:
    """A simple in-memory directed graph of PROOF relationships.

    This is a lightweight utility for working with Claim–Evidence
    Graphs locally.  It is not a database.
    """

    def __init__(self) -> None:
        self._relations: list[ProofRelation] = []

    def add(self, relation: ProofRelation) -> None:
        """Add a relationship to the graph."""
        self._relations.append(relation)

    @property
    def relations(self) -> list[ProofRelation]:
        """Return all relationships in the graph."""
        return list(self._relations)

    def find_by_source(self, source_id: str) -> list[ProofRelation]:
        """Return all relationships originating from *source_id*."""
        return [r for r in self._relations if r.source_id == source_id]

    def find_by_target(self, target_id: str) -> list[ProofRelation]:
        """Return all relationships targeting *target_id*."""
        return [r for r in self._relations if r.target_id == target_id]

    def find_by_relation(self, relation: str) -> list[ProofRelation]:
        """Return all relationships of the given type."""
        return [r for r in self._relations if r.relation == relation]

    def contradictions(self, proof_id: str) -> list[ProofRelation]:
        """Return all contradiction relationships involving *proof_id*."""
        return [
            r for r in self._relations
            if r.relation == Relation.CONTRADICTS
            and (r.source_id == proof_id or r.target_id == proof_id)
        ]

    def supporters(self, proof_id: str) -> list[ProofRelation]:
        """Return all relationships that support *proof_id*."""
        return [
            r for r in self._relations
            if r.relation in (Relation.SUPPORTS, Relation.CORROBORATES)
            and r.target_id == proof_id
        ]

    def to_dict(self) -> list[dict]:
        """Serialize all relationships to a list of dictionaries."""
        return [r.to_dict() for r in self._relations]
