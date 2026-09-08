# PROOF Protocol

> Evidence should travel with information.

PROOF is an open protocol for representing machine-readable claims
together with their evidence, attestations, temporal context, and
verification lifecycle.

PROOF does not decide what is true.

It provides a portable structure that allows independent systems to
evaluate claims and their supporting evidence.

## Why PROOF?

Information moves extremely well across the internet.

Evidence does not.

A claim can be copied thousands of times while its original source,
context, timestamp, and provenance disappear.

PROOF is designed to keep those things connected.

## Core Model

A PROOF record connects:

    CLAIM
       +
    EVIDENCE
       +
    ATTESTATION
       +
    TIME
       +
    STATUS

The result is a portable, independently verifiable provenance record.

## Example

```json
{
  "proof": "0.1",
  "id": "sha256:...",
  "claim": {
    "subject": "Acme",
    "predicate": "raised",
    "object": "USD 40 million"
  },
  "evidence": [
    {
      "type": "web",
      "source": "https://example.com/source",
      "title": "Funding announcement"
    }
  ],
  "attestations": [],
  "observed_at": "2026-09-08T00:00:00Z",
  "status": "OBSERVED"
}