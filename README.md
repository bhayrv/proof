# PROOF Protocol

> Evidence should travel with information.

PROOF is an open protocol for representing machine-readable claims
together with their evidence, attestations, temporal context, and
verification lifecycle.

PROOF does not decide what is true.

It provides a portable structure that allows independent systems to
evaluate claims and their supporting evidence.

## Status

**PROOF 0.2 — Development**

This is an experimental protocol and reference implementation. It is
not yet a finalized interoperability standard. Breaking changes may
occur between development versions.

## Why PROOF?

Information moves extremely well across the internet.

Evidence does not.

A claim can be copied thousands of times while its original source,
context, timestamp, and provenance disappear.

PROOF is designed to keep those things connected.

## What PROOF Does NOT Claim

- PROOF does not determine factual truth.
- A cryptographic signature proves key control and data integrity —
  not that the claim is true.
- PROOF does not require blockchain, tokens, or centralized services.
- PROOF is infrastructure, not an application.

## Core Data Model

A PROOF record connects:

```
CLAIM + EVIDENCE + ATTESTATION + TIME + STATUS = PROOF
```

### Claim

A machine-readable statement: subject + predicate + object.

```json
{
  "subject": "Acme Corp",
  "predicate": "raised",
  "object": "USD 40 million"
}
```

### Evidence

Material supporting a claim — URLs, documents, datasets, other PROOF records.

```json
{
  "type": "web",
  "source": "https://example.invalid/acme-funding",
  "title": "Acme Corp Series B Announcement"
}
```

### Attestation

An Ed25519 cryptographic signature binding a key to a PROOF identity.

### Lifecycle Status

```
UNKNOWN → OBSERVED → CORROBORATED → VERIFIED
                   → CONTESTED
                   → RETRACTED
                   → SUPERSEDED
```

`VERIFIED` means "accepted by a specified verification policy" — not
universal truth.

## Identity

The PROOF identity is a SHA-256 hash of the canonical representation of
the **immutable content** only:

- Protocol version (`"proof": "0.2"`)
- Claim (subject, predicate, object)
- Evidence records

Mutable fields (status, observed_at, attestations) are excluded.
Changing status does not change identity. Signatures remain valid
across lifecycle transitions.

Format: `sha256:<64 lowercase hex characters>`

## Verification

Verification produces a structured result, not a single boolean:

```json
{
  "identity_valid": true,
  "signature_valid": true,
  "evidence_present": true,
  "lifecycle_status": "OBSERVED",
  "errors": []
}
```

Verification distinguishes cryptographic validity from factual truth.

## Graph Relationships

PROOF records can be connected via typed relationships:

- `supports` / `corroborates` — positive evidence connections
- `contradicts` — conflicting claims (both can coexist)
- `supersedes` — updated versions
- `derived_from` — provenance chains

## Installation

```bash
# Install from source
git clone <repository-url>
cd proof-protocol
pip install -e ".[dev]"
```

Requires Python 3.11+.

## CLI Usage

```bash
# Create a PROOF record
proof create --subject "Acme" --predicate "raised" --object "USD 40M" \
  --evidence-type web --evidence-source "https://example.invalid/funding"

# Compute identity from JSON stdin
cat record.json | proof identity

# Sign a PROOF record
cat record.json | proof sign

# Verify a PROOF record
cat record.json | proof verify

# Inspect a PROOF record
cat record.json | proof inspect
```

All commands support JSON input/output for pipeline compatibility.

## Python API

```python
from proof import Claim, Evidence, Proof, proof_id

# Create a claim
claim = Claim(subject="Acme", predicate="raised", object="USD 40 million")

# Attach evidence
evidence = Evidence(type="web", source="https://example.invalid/funding")

# Build a PROOF record
proof = Proof(claim=claim, evidence=[evidence])
proof.id = proof_id(proof)

# Sign
from proof import create_attestation, verify_attestation
attestation, private_key = create_attestation(proof)

# Verify
assert verify_attestation(proof, attestation) is True

# Structured verification
from proof import verify_proof, Attestation
result = verify_proof(proof, attestations=[attestation])
print(result.to_dict())
```

## Examples

See the `examples/` directory:

- `basic_claim.py` — Creating a PROOF record
- `basic_claim.json` — Example record as JSON
- `attestation.py` — Signing and verification
- `contradiction.py` — Conflicting claims and graph relationships

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest -v

# Run a specific test file
python -m pytest tests/test_identity.py -v
```

## Security Model

See [SECURITY.md](SECURITY.md) for details.

Key points:

- Signatures prove key control and data integrity, not factual truth.
- Private keys are never persisted by the library.
- Timestamps are self-reported metadata, not cryptographically bound.
- The protocol is experimental.

## Versioning

The `proof` field identifies the protocol version. PROOF 0.2 records
use `"proof": "0.2"`. The version participates in identity computation
— the same claim under different versions has different identities.

## Architecture

See [docs/architecture.md](docs/architecture.md) for design decisions
including the immutable identity model and canonicalization strategy.

## Interoperability

See [`docs/interoperability.md`](docs/interoperability.md) — How PROOF maps
  to W3C PROV, C2PA, Verifiable Credentials, Sigstore, in-toto,
  and Schema.org.

## Specification

See [spec/PROOF.md](spec/PROOF.md) for the normative protocol specification.

## License

Apache-2.0 — see [LICENSE](LICENSE).