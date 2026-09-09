# PROOF Protocol

<p align="center">
  <img src="assets/proof-intro.png" alt="PROOF — Protocol for Readable Object Origin and Facts" width="100%">
</p>

<p align="center">
  <strong>Protocol for Readable Object Origin and Facts</strong><br>
  An open protocol for machine-readable claims, evidence, attestations, temporal context, and verification lifecycle.
</p>

> Evidence should travel with information.

PROOF does not decide what is true.

It provides a portable structure that allows independent systems to
evaluate claims and their supporting evidence.

## Status

**PROOF 0.2 — Development**

This is an experimental protocol and reference implementation. It is
not yet a finalized interoperability standard. Breaking changes may
occur between development versions.

## Why PROOF?

Information moves extremely well across the internet. Evidence does not.

A claim can be copied thousands of times while its original source, context, timestamp, and provenance disappear. PROOF is designed to keep those things connected. It is a neutral verification primitive for machine-readable knowledge.

**WITHOUT PROOF:**
> "Acme Corp raised $40 million."

This is just a string of text. A machine cannot verify it, know who said it, when it was said, or what evidence supports it.

**WITH PROOF:**
> `claim` + `evidence` + `observation time` + `attestation` + `status` + `relationships`

A PROOF record packages the claim with its supporting evidence, cryptographic signatures from those who attest to it, and a traceable lifecycle. It represents exactly what was claimed, what evidence was associated with it, who attested to the exact immutable payload, and what supports or contradicts it.

## What PROOF Does NOT Claim

- PROOF does not determine universal or factual truth.
- A cryptographic signature proves key control and data integrity — not that the claim is true.
- PROOF does not require blockchain, tokens, or centralized services.
- PROOF is an open infrastructure protocol, not an application.

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

## Quickstart

A developer should be able to create, sign, and verify a record in minutes.

### 1. Install

Requires Python 3.11+.

```bash
git clone https://github.com/bhayrv/proof.git
cd proof
python -m pip install .
```
*(For local development, use `python -m pip install -e ".[dev]" `)*

### 2. Create a Claim

Create a record connecting a claim to its evidence.

```bash
proof create --subject "Acme" --predicate "raised" --object "USD 40M" \
  --evidence-type web --evidence-source "https://example.invalid/funding" > record.json
```

### 3. Inspect and Compute Identity

Inspect the record and compute its immutable cryptographic identity.

```bash
cat record.json | proof inspect
cat record.json | proof identity
```

### 4. Sign and Verify

Generate an Ed25519 keypair, sign the record to attest to it, and verify the attestation.

```bash
proof keygen > keys.json
# Extract the hex private key (using jq or similar), then sign:
# (Assuming $PRIVATE_KEY contains the hex string from keys.json)
cat record.json | proof sign --private-key $PRIVATE_KEY > signed_record.json
cat signed_record.json | proof verify
```

All commands support JSON input/output for strict pipeline compatibility.

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

See the `examples/` directory for compelling real-world demonstrations of PROOF:

- `demo_financial_intelligence.py` — A financial data pipeline showing an earnings claim, multiple evidence attachments, an attestation, and a later contradictory claim (`contradicts` relation).
- `demo_temporal_supersession.py` — Demonstrates an acquisition claim being revised (`supersedes` relation), showing how a machine can trace claim history and apply an explicit consumer policy to identify the currently preferred claim.
- `demo_ai_agent_pipeline.py` — Simulates an AI extraction workflow: mock extraction → evidence association → review → attestation → deterministic verification, allowing downstream systems to verify the claimed provenance and attestation integrity without trusting the AI model itself.
- `visualizer/index.html` — A lightweight, dependency-free HTML/JS visualizer to render a PROOF graph (claims, evidence, attestations, and relationships).
- `cli_end_to_end.ps1` — A complete PowerShell script demonstrating the full CLI lifecycle.

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