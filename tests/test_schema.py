"""
PROOF Protocol — Schema Validation Tests

Validates representative PROOF documents against the JSON Schema
defined in spec/schema.json.
"""

import json
import pathlib

import pytest

jsonschema = pytest.importorskip("jsonschema")

SCHEMA_PATH = pathlib.Path(__file__).resolve().parent.parent / "spec" / "schema.json"


@pytest.fixture
def schema():
    """Load the PROOF 0.2 JSON Schema."""
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def _validate(instance: dict, schema: dict) -> None:
    jsonschema.validate(instance=instance, schema=schema)


class TestSchemaValidRecords:
    """Valid PROOF records must pass schema validation."""

    def test_minimal_record(self, schema):
        record = {
            "proof": "0.2",
            "claim": {"subject": "Acme", "predicate": "raised", "object": "USD 40M"},
            "evidence": [],
            "status": "OBSERVED",
        }
        _validate(record, schema)

    def test_full_record(self, schema):
        record = {
            "proof": "0.2",
            "id": "sha256:" + "a" * 64,
            "claim": {"subject": "Acme", "predicate": "raised", "object": "USD 40M"},
            "evidence": [
                {
                    "type": "web",
                    "source": "https://example.invalid/funding",
                    "title": "Funding announcement",
                    "observed_at": "2026-09-08T00:00:00Z",
                }
            ],
            "attestations": [
                {
                    "proof_id": "sha256:" + "a" * 64,
                    "algorithm": "Ed25519",
                    "public_key": "b" * 64,
                    "signature": "c" * 128,
                    "created_at": "2026-09-08T00:00:00Z",
                }
            ],
            "observed_at": "2026-09-08T00:00:00Z",
            "status": "VERIFIED",
        }
        _validate(record, schema)

    def test_structured_object_value(self, schema):
        record = {
            "proof": "0.2",
            "claim": {
                "subject": "Acme",
                "predicate": "reported",
                "object": {"revenue": 1000000, "currency": "USD"},
            },
            "evidence": [],
            "status": "OBSERVED",
        }
        _validate(record, schema)

    def test_all_status_values(self, schema):
        for status in [
            "UNKNOWN", "OBSERVED", "CORROBORATED",
            "VERIFIED", "CONTESTED", "RETRACTED", "SUPERSEDED",
        ]:
            record = {
                "proof": "0.2",
                "claim": {"subject": "X", "predicate": "is", "object": "Y"},
                "evidence": [],
                "status": status,
            }
            _validate(record, schema)


class TestSchemaInvalidRecords:
    """Invalid PROOF records must fail schema validation."""

    def test_missing_claim(self, schema):
        record = {
            "proof": "0.2",
            "evidence": [],
            "status": "OBSERVED",
        }
        with pytest.raises(jsonschema.ValidationError):
            _validate(record, schema)

    def test_missing_evidence(self, schema):
        record = {
            "proof": "0.2",
            "claim": {"subject": "X", "predicate": "is", "object": "Y"},
            "status": "OBSERVED",
        }
        with pytest.raises(jsonschema.ValidationError):
            _validate(record, schema)

    def test_wrong_protocol_version(self, schema):
        record = {
            "proof": "0.1",
            "claim": {"subject": "X", "predicate": "is", "object": "Y"},
            "evidence": [],
            "status": "OBSERVED",
        }
        with pytest.raises(jsonschema.ValidationError):
            _validate(record, schema)

    def test_invalid_status(self, schema):
        record = {
            "proof": "0.2",
            "claim": {"subject": "X", "predicate": "is", "object": "Y"},
            "evidence": [],
            "status": "INVALID_STATUS",
        }
        with pytest.raises(jsonschema.ValidationError):
            _validate(record, schema)

    def test_malformed_identity(self, schema):
        record = {
            "proof": "0.2",
            "id": "not_a_valid_hash",
            "claim": {"subject": "X", "predicate": "is", "object": "Y"},
            "evidence": [],
            "status": "OBSERVED",
        }
        with pytest.raises(jsonschema.ValidationError):
            _validate(record, schema)

    def test_claim_missing_subject(self, schema):
        record = {
            "proof": "0.2",
            "claim": {"predicate": "is", "object": "Y"},
            "evidence": [],
            "status": "OBSERVED",
        }
        with pytest.raises(jsonschema.ValidationError):
            _validate(record, schema)

    def test_invalid_attestation_algorithm(self, schema):
        record = {
            "proof": "0.2",
            "claim": {"subject": "X", "predicate": "is", "object": "Y"},
            "evidence": [],
            "attestations": [
                {
                    "proof_id": "sha256:" + "a" * 64,
                    "algorithm": "RSA-2048",
                    "public_key": "b" * 64,
                    "signature": "c" * 128,
                }
            ],
            "status": "OBSERVED",
        }
        with pytest.raises(jsonschema.ValidationError):
            _validate(record, schema)
