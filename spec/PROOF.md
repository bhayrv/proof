# PROOF Protocol Specification

## Status

PROOF 0.2 — Development

This specification defines the PROOF 0.2 data model, identity semantics,
canonicalization rules, attestation format, lifecycle states, graph
relationships, and verification semantics.

PROOF 0.2 is not yet a finalized interoperability standard.

---

## 1. Purpose

PROOF is an open protocol for representing machine-readable claims
together with their evidence, attestations, temporal context, and
verification lifecycle.

PROOF does not determine truth.

It provides a portable structure that allows independent systems to
evaluate a claim and its supporting evidence.

> Evidence should travel with information.

---

## 2. Design Principles

### 2.1 Evidence travels with information

A claim should remain connected to the evidence associated with it.

### 2.2 Signatures are not truth

A cryptographic signature proves control of a signing key and integrity
of the signed bytes.

A valid signature does NOT prove that the underlying claim is factually
true.

### 2.3 Unknown is valid

Absence of evidence must not automatically be interpreted as evidence
of falsity or truth.

Systems implementing PROOF should preserve explicit uncertainty.

### 2.4 Vendor neutral

PROOF is not tied to a particular cloud provider, database, AI model,
blockchain, application, or identity provider.

### 2.5 Local-first

The core protocol can be implemented without a centralized service.

### 2.6 Composable

PROOF records may reference other records, allowing larger
Claim–Evidence Graphs to be constructed.

### 2.7 Deterministic

The same logical content must always produce the same canonical bytes,
the same identity, and the same verification result.

---

## 3. Protocol Objects

### 3.1 PROOF Record

A PROOF record is a JSON object with the following structure:

```json
{
  "proof": "0.2",
  "id": "sha256:<hex>",
  "claim": { ... },
  "evidence": [ ... ],
  "attestations": [ ... ],
  "observed_at": "<ISO 8601 timestamp or null>",
  "status": "<lifecycle status>"
}
```

#### Required fields

| Field         | Type     | Description                              |
|---------------|----------|------------------------------------------|
| `proof`       | string   | Protocol version. Must be `"0.2"`.       |
| `claim`       | object   | The claim being made. See §3.2.          |
| `evidence`    | array    | Evidence records. See §3.3. May be empty.|
| `status`      | string   | Lifecycle status. See §6. Default: `"OBSERVED"`. |

#### Optional fields

| Field          | Type           | Description                         |
|----------------|----------------|-------------------------------------|
| `id`           | string or null | Content identity. See §4.           |
| `attestations` | array          | Attestation records. See §5.        |
| `observed_at`  | string or null | ISO 8601 timestamp of first observation. |

### 3.2 Claim

A claim is a machine-readable statement consisting of three components:

```json
{
  "subject": "<string>",
  "predicate": "<string>",
  "object": <value>
}
```

| Field       | Type   | Description                                    |
|-------------|--------|------------------------------------------------|
| `subject`   | string | The entity the claim is about.                 |
| `predicate` | string | The relationship or action being asserted.     |
| `object`    | any    | The value of the assertion. See §4.3 for type restrictions. |

The `object` field supports any JSON-compatible value: strings, integers
(within the interoperable range), booleans, null, arrays, and objects.

### 3.3 Evidence

An evidence record describes material supporting a claim:

```json
{
  "type": "<string>",
  "source": "<string>",
  "title": "<string>",
  "content_hash": "<string>",
  "observed_at": "<ISO 8601>",
  "metadata": { ... }
}
```

| Field          | Type           | Required | Description                     |
|----------------|----------------|----------|---------------------------------|
| `type`         | string         | yes      | Category of evidence (e.g., `"web"`, `"document"`, `"api"`, `"dataset"`, `"proof"`). |
| `source`       | string         | yes      | URI, identifier, or location of the evidence. |
| `title`        | string or null | no       | Human-readable title.           |
| `content_hash` | string or null | no       | Content hash for integrity (format: `"sha256:<hex>"`). |
| `observed_at`  | string or null | no       | ISO 8601 timestamp of observation. |
| `metadata`     | object or null | no       | Additional structured metadata. |

Evidence records participate in identity computation (§4).

---

## 4. Identity

### 4.1 Immutable content identity

The PROOF identity is a cryptographic hash derived exclusively from
immutable content. The identity is deterministic: the same logical
content always produces the same identity.

#### Identity-participating fields

The identity is computed from a JSON object containing exactly:

```json
{
  "proof": "0.2",
  "claim": { "subject": "...", "predicate": "...", "object": ... },
  "evidence": [ ... ]
}
```

The following fields are **excluded** from identity computation:

- `id` — the identity itself (self-referential exclusion)
- `status` — mutable lifecycle state
- `observed_at` — observation metadata
- `attestations` — added after creation

**Rationale:** A claim's identity represents *what is being claimed and
what evidence supports it*. Lifecycle transitions (e.g., OBSERVED →
VERIFIED) and attestations are events *about* the claim, not the claim
itself. Including mutable fields in identity would invalidate all
previous attestations on any status change, making the protocol unusable.

### 4.2 Identity computation

1. Construct the identity payload object (§4.1).
2. Canonicalize the payload to bytes (§4.4).
3. Compute SHA-256 over the canonical bytes.
4. Format as: `sha256:<64 lowercase hexadecimal characters>`

The identity is self-consistent: attaching the `id` field to a PROOF
record does not change the identity.

### 4.3 Interoperable value types

All values in identity-participating fields MUST be one of:

| JSON type | Constraint                                          |
|-----------|-----------------------------------------------------|
| string    | Valid Unicode. Serialized per §4.4.                 |
| integer   | Within the safe integer range: [-(2^53 - 1), 2^53 - 1] (i.e., -9007199254740991 to 9007199254740991). |
| boolean   | `true` or `false`                                   |
| null      | `null`                                              |
| array     | Elements must be interoperable types.               |
| object    | Keys must be strings. Values must be interoperable types. |

**Excluded types:**

- IEEE 754 floating-point values (use string representation instead)
- `NaN`, `Infinity`, `-Infinity` (not valid JSON)
- Values outside the safe integer range (use string representation)

**Rationale:** Floating-point serialization varies across languages and
runtimes. Restricting to safe integers ensures that every conformant
implementation produces identical canonical bytes for the same logical
value. The safe integer range corresponds to IEEE 754 double-precision
exact integer representation, matching JavaScript's `Number.MAX_SAFE_INTEGER`.

### 4.4 Canonicalization

PROOF 0.2 defines a strictly constrained canonical JSON serialization profile for identity computation and attestation signing, the **PROOF Constrained Canonical JSON Profile**.

#### Rules

1. **Encoding:** UTF-8, no byte order mark.
2. **Whitespace:** No insignificant whitespace between tokens. Separators are strictly `,` (comma) between elements and `:` (colon) between key and value.
3. **Object key ordering:** Object keys MUST be sorted lexicographically by Unicode scalar value (Unicode code point order).
4. **Strings and Escaping:** Strings are enclosed in double quotes (`"`). Escaping is strictly defined as follows:
   - Quotation mark (`"`, U+0022) is escaped as `\"`.
   - Reverse solidus/backslash (`\`, U+005C) is escaped as `\\`.
   - Backspace (U+0008) is escaped as `\b`.
   - Form feed (U+000C) is escaped as `\f`.
   - Line feed (U+000A) is escaped as `\n`.
   - Carriage return (U+000D) is escaped as `\r`.
   - Character tabulation/tab (U+0009) is escaped as `\t`.
   - All other control characters from U+0000 through U+001F MUST be escaped using six-character lowercase hexadecimal Unicode escape sequences (`\u0000` through `\u001f` excluding the short escapes above).
   - Unicode scalar values are U+0000 through U+10FFFF, excluding surrogate code points U+D800 through U+DFFF. Valid Unicode scalar values are permitted subject to the JSON escaping rules.
   - Surrogate code points U+D800 through U+DFFF MUST NOT appear as literal Unicode scalar values. Do not claim that arbitrary surrogate code points are valid UTF-8 characters.
   - Supplementary Unicode characters (U+10000 through U+10FFFF) MUST be encoded as their normal UTF-8 encoding.
5. **Numbers:** Integers only within the safe range (§4.3). No leading zeros (except for exactly `0`). Negative numbers use a leading `-`. No decimal point. No exponent notation.
6. **Booleans:** `true` or `false` (lowercase).
7. **Null:** `null` (lowercase).
8. **Arrays:** Ordered. Elements serialized in order.

#### Independence from Generic Canonicalization Schemes

This profile is inspired by prior art in deterministic JSON canonicalization but **does not claim generic conformance** to standards like RFC 8785 (JCS). Specifically, PROOF 0.2 rejects the complex parsing and formatting rules for floating-point values required by full JCS implementations. By strictly banning floats, the PROOF profile avoids the most fragile edge cases of JSON interoperability.

#### Cross-language reproducibility

Any implementation that follows the rules above will produce identical bytes for the same input. For example, in Python, this behavior is natively achieved using:

```python
json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
```

Conformance test vectors are provided in `spec/test-vectors/` and serve as the authoritative reference.

---

## 5. Attestations

### 5.1 Structure

An attestation is a cryptographic signature binding a key to a specific
PROOF identity:

```json
{
  "proof_id": "sha256:<hex>",
  "algorithm": "Ed25519",
  "public_key": "<hex>",
  "signature": "<hex>",
  "created_at": "<ISO 8601>"
}
```

| Field        | Type           | Required | Description                       |
|--------------|----------------|----------|-----------------------------------|
| `proof_id`   | string         | yes      | The PROOF identity being attested.|
| `algorithm`  | string         | yes      | Signing algorithm. Currently only `"Ed25519"`. |
| `public_key` | string         | yes      | Public key, hex-encoded raw bytes (32 bytes for Ed25519). |
| `signature`  | string         | yes      | Signature, hex-encoded raw bytes (64 bytes for Ed25519). |
| `created_at` | string or null | no       | ISO 8601 timestamp of attestation creation. |

### 5.2 Signing payload

The signing payload is the **canonical bytes of the identity payload**
(§4.1, §4.4) — the same bytes used to compute the PROOF identity.

This means:

1. The signature binds to the immutable content (claim + evidence +
   protocol version).
2. The signature remains valid across lifecycle changes (`status`),
   observation metadata changes (`observed_at`), and additional
   attestations.
3. The `proof_id` field in the attestation provides a redundant integrity
   check: verifiers should confirm that the identity computed from the
   payload matches the `proof_id` before checking the signature.

### 5.3 Verification semantics

To verify an attestation:

1. Compute the identity payload from the PROOF record (§4.1).
2. Compute the identity from the payload (§4.2).
3. Verify that `attestation.proof_id` matches the computed identity.
4. Canonicalize the identity payload (§4.4).
5. Verify the Ed25519 signature over the canonical bytes using the
   public key from the attestation.

A valid signature proves:

- The signer controlled the private key corresponding to `public_key`.
- The canonical identity payload bytes have not been modified.

A valid signature does NOT prove:

- That the claim is factually true.
- That the evidence is authentic or complete.
- The real-world identity of the signer.
- That the timestamp is accurate.

### 5.4 Key management

The PROOF protocol does not specify key management. Implementations
should:

- Allow callers to provide externally managed signing keys.
- Never persist private keys unnecessarily.
- Provide convenience key-generation helpers for testing/examples only.

---

## 6. Lifecycle

### 6.1 States

PROOF defines the following lifecycle states:

| State          | Meaning                                              |
|----------------|------------------------------------------------------|
| `UNKNOWN`      | Status has not been determined.                      |
| `OBSERVED`     | The claim has been recorded but not yet evaluated.   |
| `CORROBORATED` | Additional evidence supports the claim.              |
| `VERIFIED`     | Accepted by a specified verification policy/process. |
| `CONTESTED`    | Conflicting evidence or claims exist.                |
| `RETRACTED`    | The claim has been withdrawn by its source.          |
| `SUPERSEDED`   | Replaced by a newer version of the claim.            |

### 6.2 VERIFIED semantics

`VERIFIED` means that a specific verification policy or process has
accepted the claim based on available evidence. It does NOT mean:

- Universal or metaphysical truth.
- Consensus of all parties.
- Permanent validity.

Systems using PROOF should document their verification policies
separately from the protocol itself.

### 6.3 Lifecycle and identity

Lifecycle status is **excluded** from identity computation. Changing the
status of a PROOF record does not change its identity and does not
invalidate existing attestations.

This is a deliberate design choice: the identity represents *what* is
claimed, not *what we currently think about it*.

### 6.4 Temporal metadata

| Timestamp          | Semantics                                             |
|--------------------|-------------------------------------------------------|
| `observed_at`      | When the claim was first recorded/observed. Set once.  |
| `attestation.created_at` | When a specific attestation was created.         |

Timestamps are ISO 8601 strings (e.g., `"2026-09-08T12:00:00Z"`).
Timestamps are metadata — they are not cryptographically bound to the
claim unless they appear inside the claim's `object` field.

---

## 7. Graph Relationships

### 7.1 Relationship types

PROOF records may be connected via typed relationships:

| Relationship   | Meaning                                              |
|----------------|------------------------------------------------------|
| `supports`     | Source provides supporting evidence for target.       |
| `contradicts`  | Source presents evidence contradicting target.        |
| `supersedes`   | Source is an updated version of target.               |
| `derived_from` | Source was derived from or based on target.           |
| `corroborates` | Source independently confirms target.                |

### 7.2 Relationship structure

```json
{
  "source_id": "sha256:<hex>",
  "target_id": "sha256:<hex>",
  "relation": "<relationship type>",
  "metadata": { ... }
}
```

| Field       | Type           | Required | Description                      |
|-------------|----------------|----------|----------------------------------|
| `source_id` | string         | yes      | PROOF identity of the source.    |
| `target_id` | string         | yes      | PROOF identity of the target.    |
| `relation`  | string         | yes      | One of the defined relationship types. |
| `metadata`  | object or null | no       | Additional relationship metadata.|

### 7.3 Contradiction semantics

PROOF can represent conflicting claims without forcing either to be
"truth". Two PROOF records with contradictory claims can both exist with
a `contradicts` relationship between them. Resolution is left to
verification policies, not the protocol.

---

## 8. Verification

### 8.1 Verification result

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

| Field             | Type    | Description                                |
|-------------------|---------|--------------------------------------------|
| `identity_valid`  | boolean | The `id` field matches computed identity.  |
| `signature_valid` | boolean | All attestation signatures verify.         |
| `evidence_present`| boolean | At least one evidence record exists.       |
| `lifecycle_status`| string  | Current lifecycle status.                  |
| `errors`          | array   | List of error/warning strings.             |

### 8.2 Verification semantics

Verification distinguishes:

- **Cryptographic validity:** Is the identity correct? Do signatures verify?
- **Evidence presence:** Is there evidence to evaluate?
- **Lifecycle status:** What is the current state of the claim?

Verification does NOT determine:

- Whether the claim is factually true.
- Whether the evidence is authentic.
- Whether the signer is trustworthy.

---

## 9. Versioning

The `proof` field identifies the protocol version. PROOF 0.2 records
use `"proof": "0.2"`.

The protocol version participates in identity computation. The same
claim+evidence under different protocol versions will have different
identities. This is intentional: it provides protocol-version namespace
separation.

### 9.1 Extensibility

Future protocol versions may add fields to any object. Implementations
should:

- Ignore unknown fields when reading.
- Preserve unknown fields when round-tripping.
- Only include defined fields in identity computation.

---

## 10. Security Considerations

See SECURITY.md for detailed security documentation.

Key points:

- Signatures prove key control and data integrity, not factual truth.
- Private keys must be handled securely by the application layer.
- Timestamps are not cryptographically bound unless included in claim content.
- The protocol is experimental and should not be used for security-critical
  applications without additional review.

---

## 11. Scope Exclusions

PROOF does not require and does not specify:

- Blockchain or distributed ledger
- Cryptocurrency or tokens
- Centralized registry or database
- Proprietary AI models
- Cloud services
- Key management infrastructure
- Trust frameworks

These may be built on top of the protocol but are not part of it.