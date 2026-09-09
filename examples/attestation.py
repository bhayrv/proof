"""
PROOF Protocol — Attestation Example

Creates a PROOF record, signs it with an Ed25519 key, and verifies
the attestation.

Usage:
    python examples/attestation.py
"""

import json

from proof import (
    Attestation,
    Claim,
    Evidence,
    Proof,
    create_attestation,
    proof_id,
    verify_attestation,
    verify_proof,
)

# 1. Create the PROOF record
claim = Claim(
    subject="Globex Industries",
    predicate="acquired",
    object="Widget Co",
)

evidence = Evidence(
    type="document",
    source="https://example.invalid/globex-acquisition.pdf",
    title="Acquisition agreement",
)

proof = Proof(
    claim=claim,
    evidence=[evidence],
    observed_at="2026-09-08T15:30:00Z",
)

proof.id = proof_id(proof)
print("PROOF record created.")
print(f"Identity: {proof.id}\n")

# 2. Sign the record (generates a new key for this example)
attestation, private_key_bytes = create_attestation(
    proof,
    created_at="2026-09-08T15:31:00Z",
)

print("Attestation created:")
print(json.dumps(attestation.to_dict(), indent=2))
print(f"\nPrivate key (hex): {private_key_bytes.hex()}")
print("  (In production, store this securely!)\n")

# 3. Verify the attestation
is_valid = verify_attestation(proof, attestation)
print(f"Signature valid: {is_valid}")

# 4. Structured verification
att_list = [attestation]
result = verify_proof(proof, attestations=att_list)
print(f"\nVerification result:")
print(json.dumps(result.to_dict(), indent=2))

# 5. Demonstrate tamper detection
print("\n--- Tamper detection ---")
proof.claim.object = "Fake Co"
is_valid_after_tamper = verify_attestation(proof, attestation)
print(f"Signature valid after tampering: {is_valid_after_tamper}")
