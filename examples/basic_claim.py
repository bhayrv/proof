"""
PROOF Protocol — Basic Claim Example

Creates a simple PROOF record, computes its identity, and prints
the result as JSON.

Usage:
    python examples/basic_claim.py
"""

from proof import Claim, Evidence, Proof, proof_id

# 1. Create a claim
claim = Claim(
    subject="Acme Corp",
    predicate="raised",
    object="USD 40 million",
)

# 2. Attach evidence
evidence = Evidence(
    type="web",
    source="https://example.invalid/acme-funding",
    title="Acme Corp Series B Announcement",
    observed_at="2026-09-08T12:00:00Z",
)

# 3. Build the PROOF record
proof = Proof(
    claim=claim,
    evidence=[evidence],
    observed_at="2026-09-08T12:00:00Z",
)

# 4. Compute and attach the content identity
proof.id = proof_id(proof)

# 5. Output
import json

print(json.dumps(proof.to_dict(), indent=2))
print(f"\nIdentity: {proof.id}")
