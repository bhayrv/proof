"""
PROOF Protocol — Lifecycle

Defines the lifecycle states and valid transitions for PROOF records.

Lifecycle state is metadata about a claim — it is explicitly excluded
from identity computation so that state changes do not invalidate
existing attestations.

See spec/PROOF.md §6 for the normative specification.
"""

from __future__ import annotations

from enum import Enum


class Status(str, Enum):
    """PROOF lifecycle states.

    Each state describes the current disposition of a claim.  The
    protocol defines states but does NOT imply that any state
    represents universal or metaphysical truth.

    ``VERIFIED`` means *accepted by a specified verification
    policy/process* — nothing more.
    """

    UNKNOWN = "UNKNOWN"
    OBSERVED = "OBSERVED"
    CORROBORATED = "CORROBORATED"
    VERIFIED = "VERIFIED"
    CONTESTED = "CONTESTED"
    RETRACTED = "RETRACTED"
    SUPERSEDED = "SUPERSEDED"


# Valid state transitions.
# Each key maps to the set of states reachable from it.
VALID_TRANSITIONS: dict[Status, frozenset[Status]] = {
    Status.UNKNOWN: frozenset({
        Status.OBSERVED,
    }),
    Status.OBSERVED: frozenset({
        Status.CORROBORATED,
        Status.VERIFIED,
        Status.CONTESTED,
        Status.RETRACTED,
        Status.SUPERSEDED,
    }),
    Status.CORROBORATED: frozenset({
        Status.VERIFIED,
        Status.CONTESTED,
        Status.RETRACTED,
        Status.SUPERSEDED,
    }),
    Status.VERIFIED: frozenset({
        Status.CONTESTED,
        Status.RETRACTED,
        Status.SUPERSEDED,
    }),
    Status.CONTESTED: frozenset({
        Status.VERIFIED,
        Status.RETRACTED,
        Status.SUPERSEDED,
    }),
    Status.RETRACTED: frozenset({
        Status.SUPERSEDED,
    }),
    Status.SUPERSEDED: frozenset(),
}


def is_valid_transition(from_status: Status, to_status: Status) -> bool:
    """Return True if *from_status* → *to_status* is a valid transition."""
    return to_status in VALID_TRANSITIONS.get(from_status, frozenset())
