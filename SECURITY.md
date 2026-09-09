# SECURITY.md

## Experimental Status

PROOF 0.2 is an experimental protocol. It has not undergone formal
security audit. Do not use it for security-critical applications
without additional review.

## Cryptographic Assumptions

### Hash Function

PROOF uses SHA-256 for content identity. SHA-256 is widely regarded
as collision-resistant and preimage-resistant for the foreseeable
future. If SHA-256 is eventually weakened, the protocol will need
to migrate to a stronger hash function via a version bump.

### Digital Signatures

PROOF uses Ed25519 (Curve25519 + SHA-512) for attestation signatures.
Ed25519 provides 128-bit security against classical attacks.

The reference implementation uses the `cryptography` Python library,
which wraps OpenSSL's Ed25519 implementation.

## What Signatures Prove

A valid PROOF attestation signature proves:

1. **Key control**: The signer controlled the Ed25519 private key
   corresponding to the public key in the attestation.
2. **Data integrity**: The canonical identity payload bytes
   (protocol version, claim, evidence) have not been modified since
   signing.

A valid signature does **NOT** prove:

- That the claim is factually true.
- That the evidence is authentic or complete.
- The real-world identity of the signer.
- That the timestamps are accurate.
- That the claim has been verified by any authority.

## Private Key Handling

- The PROOF protocol does not specify key management.
- The reference implementation never persists private keys to disk
  unless the caller explicitly does so.
- The `create_attestation()` function returns private key bytes so
  the caller can securely store them. These bytes should be treated
  as secrets.
- The convenience `generate_private_key()` function is intended for
  testing and examples only. Production systems should use externally
  managed keys.
- Private keys must never be committed to version control.

## Canonicalization

The canonical JSON serialization is deterministic within the
restricted type set (no floating-point values). PROOF uses its
own Constrained Canonical JSON Profile. Independent implementations 
must follow the exact rules in `spec/PROOF.md §4.4` to produce 
matching bytes.

## Timestamp Trust

Timestamps in PROOF records (`observed_at`, `created_at`) are
self-reported metadata. They are not cryptographically bound to
the claim unless they appear inside the claim's `object` field.
Implementations should not trust timestamps without external
verification.

## Denial of Service

The current implementation does not enforce size limits on claims,
evidence records, or metadata objects. Applications processing
untrusted PROOF records should impose their own limits.

## Reporting Security Vulnerabilities

If you discover a security vulnerability in the PROOF protocol
or reference implementation, please report it responsibly.

Until a dedicated security contact is established, please open
a private security advisory on the project's GitHub repository
or contact the project maintainers directly.

Do not disclose security vulnerabilities in public issues.
