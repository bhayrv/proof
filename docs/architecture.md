# PROOF Protocol — Architecture

## Overview

PROOF is an open protocol for representing machine-readable claims
together with their evidence, attestations, and verification lifecycle.

This document describes the architectural decisions behind PROOF 0.2.

## Immutable vs Mutable Identity

### The Problem

In PROOF 0.1, the identity was computed by hashing the entire record
including mutable fields (`status`, `observed_at`, `attestations`).
This meant that any lifecycle change — such as moving a claim from
`OBSERVED` to `VERIFIED` — would change its identity and invalidate
all existing attestations.

### The Solution

PROOF 0.2 separates identity into two layers:

1. **Immutable content identity**: Computed from protocol version,
   claim, and evidence only. These fields are fixed at creation time.
2. **Mutable lifecycle metadata**: Status, observation timestamp,
   and attestations are excluded from identity computation.

This means:

- Changing status does not change identity.
- Adding attestations does not change identity.
- Signatures remain valid across lifecycle transitions.
- The identity represents *what is being claimed*, not *what we
  currently think about it*.

### Identity Computation

```
identity_payload = {
    "proof": "0.2",
    "claim": { subject, predicate, object },
    "evidence": [ { type, source, ... }, ... ]
}

canonical_bytes = canonicalize(identity_payload)
identity = "sha256:" + SHA-256(canonical_bytes).hex()
```

## Canonicalization

PROOF 0.2 uses the **PROOF Constrained Canonical JSON Profile** for deterministic serialization:

- Sorted keys (lexicographic by Unicode code point)
- No insignificant whitespace
- UTF-8 encoding
- Strict control character escaping
- No floating-point numbers (integers only within safe range)

By strictly banning floating-point numbers, PROOF avoids the hardest canonicalization problem (IEEE 754 serialization varies across languages) while keeping the protocol simple and deterministic. It does not claim generic conformance to RFC 8785/JCS.

### Safe Integer Range

Values outside [-(2^53 - 1), 2^53 - 1] must be represented as
strings. This range corresponds to IEEE 754 double-precision exact
integer representation and JavaScript's `Number.MAX_SAFE_INTEGER`.

## Attestation Signing

The signing payload is the **canonical bytes of the identity payload**
— the same bytes used to compute the identity. This means:

1. The signature binds to immutable content only.
2. Status changes do not invalidate signatures.

## Conceptual Separation

PROOF explicitly separates several distinct concepts:

- **Content Identity:** Stable content addressing (the SHA-256 hash).
- **Attestation:** Signer binding and integrity (the Ed25519 signature). Identity and attestation are distinct; the identity is not merely redundant to the signature but serves as the stable address of the content.
- **Observation:** The real-world act of witnessing or recording an event (`observed_at`).
- **Verification Event:** The procedural, mechanical verification of structural and cryptographic validity.
- **Lifecycle State:** The current disposition of the claim (`status`).

## Lifecycle

Lifecycle states describe the current disposition of a claim.
They are metadata about the claim, not part of the claim itself.

State transitions are validated but not enforced at the protocol
level — applications can choose their own policies.

`VERIFIED` means "accepted by a specified verification policy" — it
explicitly does NOT mean universal or metaphysical truth.

## Graph Relationships

PROOF supports typed relationships between records:

- `supports` / `corroborates` — positive evidence connections
- `contradicts` — conflicting claims
- `supersedes` — version chains
- `derived_from` — provenance chains

The protocol defines the relationship representation. Graph storage
and query are application concerns.

## Module Structure

```
proof/
    __init__.py      — Public API exports
    models.py        — Claim, Proof dataclasses
    evidence.py      — Evidence dataclass
    identity.py      — Identity computation
    canonical.py     — Canonical JSON serialization
    crypto.py        — SHA-256, Ed25519 primitives
    attestation.py   — Attestation creation/verification
    lifecycle.py     — Status enum, transitions
    graph.py         — Relationship types, in-memory graph
    verify.py        — Structured verification
    cli.py           — Command-line interface
```
