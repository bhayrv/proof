# PROOF Protocol

## Status

PROOF 0.1 — Experimental

## Purpose

PROOF is an open protocol for representing machine-readable claims
together with their evidence, attestations, temporal context, and
verification lifecycle.

PROOF does not determine truth.

It represents the information required for independent systems to
evaluate a claim.

---

## Core Object

A PROOF record contains:

- a protocol version
- a content-derived identity
- a claim
- zero or more evidence records
- zero or more attestations
- an observation timestamp
- a lifecycle status

Conceptually:

    Claim
      +
    Evidence
      +
    Attestation
      +
    Time
      +
    Status
      =
    PROOF

---

## Claim

A claim consists of three components:

- `subject`
- `predicate`
- `object`

Example:

```json
{
  "subject": "Acme",
  "predicate": "raised",
  "object": "USD 40 million"
}