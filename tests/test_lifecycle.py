"""
PROOF Protocol — Lifecycle Tests

Tests lifecycle states and transitions defined in spec/PROOF.md §6.
"""

import pytest

from proof.lifecycle import Status, VALID_TRANSITIONS, is_valid_transition


class TestStatusEnum:
    """Tests for the Status enum."""

    def test_all_states_defined(self):
        expected = {
            "UNKNOWN", "OBSERVED", "CORROBORATED",
            "VERIFIED", "CONTESTED", "RETRACTED", "SUPERSEDED",
        }
        actual = {s.value for s in Status}
        assert actual == expected

    def test_status_is_string(self):
        """Status values should be usable as strings."""
        assert Status.OBSERVED.value == "OBSERVED"
        assert Status.VERIFIED.value == "VERIFIED"

    def test_status_from_string(self):
        assert Status("OBSERVED") == Status.OBSERVED
        assert Status("VERIFIED") == Status.VERIFIED

    def test_invalid_status_raises(self):
        with pytest.raises(ValueError):
            Status("INVALID_STATE")


class TestTransitions:
    """Tests for lifecycle state transitions."""

    def test_unknown_to_observed(self):
        assert is_valid_transition(Status.UNKNOWN, Status.OBSERVED) is True

    def test_unknown_to_verified_invalid(self):
        assert is_valid_transition(Status.UNKNOWN, Status.VERIFIED) is False

    def test_observed_to_verified(self):
        assert is_valid_transition(Status.OBSERVED, Status.VERIFIED) is True

    def test_observed_to_contested(self):
        assert is_valid_transition(Status.OBSERVED, Status.CONTESTED) is True

    def test_observed_to_retracted(self):
        assert is_valid_transition(Status.OBSERVED, Status.RETRACTED) is True

    def test_verified_to_contested(self):
        assert is_valid_transition(Status.VERIFIED, Status.CONTESTED) is True

    def test_verified_to_retracted(self):
        assert is_valid_transition(Status.VERIFIED, Status.RETRACTED) is True

    def test_contested_to_verified(self):
        """A contested claim can be re-verified."""
        assert is_valid_transition(Status.CONTESTED, Status.VERIFIED) is True

    def test_retracted_to_superseded(self):
        assert is_valid_transition(Status.RETRACTED, Status.SUPERSEDED) is True

    def test_retracted_to_verified_invalid(self):
        """A retracted claim cannot be directly re-verified."""
        assert is_valid_transition(Status.RETRACTED, Status.VERIFIED) is False

    def test_superseded_is_terminal(self):
        """SUPERSEDED is a terminal state — no transitions out."""
        for status in Status:
            assert is_valid_transition(Status.SUPERSEDED, status) is False

    def test_all_states_have_transition_rules(self):
        """Every state must appear in the transition table."""
        for status in Status:
            assert status in VALID_TRANSITIONS
