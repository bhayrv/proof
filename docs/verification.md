# PROOF Protocol — Verification Semantics

## Principles

PROOF verification distinguishes **cryptographic validity** from
**factual truth**.

Verification answers structural questions:

- Is the identity valid?
- Do signatures verify?
- Is evidence present?
- What is the lifecycle status?

Verification does NOT answer:

- Is the claim factually true?
- Is the evidence authentic?
- Is the signer trustworthy?
- Should I believe this claim?

## Verification Dimensions

### Identity Valid

Does the `id` field match the SHA-256 hash of the canonical identity
payload (protocol version + claim + evidence)?

A mismatch indicates data corruption or tampering.

### Signature Valid

For each attestation:

1. Does `attestation.proof_id` match the computed identity?
2. Does the Ed25519 signature verify against the canonical identity
   payload bytes using the given public key?

A valid signature proves key control and data integrity.
An invalid signature indicates tampering, corruption, or key mismatch.

### Evidence Present

Does the record contain at least one evidence record?

A claim without evidence is valid but less useful. PROOF does not
require evidence — it simply reports its absence.

### Lifecycle Status

What is the current status of the claim (OBSERVED, VERIFIED, etc.)?

PROOF reports the status but does not interpret it. A `VERIFIED`
status means a verification policy accepted the claim — the
verifier must decide whether to trust that policy.

## Verification Result

```json
{
  "identity_valid": true,
  "signature_valid": true,
  "evidence_present": true,
  "lifecycle_status": "OBSERVED",
  "errors": []
}
```

An empty `errors` array indicates no structural problems were found.
The consumer must still apply their own trust decisions.

## Trust Decisions

PROOF deliberately separates verification from trust:

- **Verification** is mechanical and deterministic.
- **Trust** requires policy decisions that are outside the protocol.

Examples of trust decisions NOT made by PROOF:

- "Is this public key associated with a known organization?"
- "Is this evidence source reliable?"
- "Should I accept claims with status VERIFIED?"
- "How many attestations are required?"

These are application-level concerns.
