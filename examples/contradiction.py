"""
PROOF Protocol — Contradiction Example

Demonstrates how PROOF represents conflicting claims without
forcing either to be "truth".

Usage:
    python examples/contradiction.py
"""

import json

from proof import (
    Claim,
    Evidence,
    Proof,
    ProofGraph,
    ProofRelation,
    Relation,
    proof_id,
)

# 1. Claim A: Company reports revenue of USD 50 million
claim_a = Claim(
    subject="MegaCorp",
    predicate="reported_revenue",
    object="USD 50 million",
)
proof_a = Proof(
    claim=claim_a,
    evidence=[
        Evidence(
            type="document",
            source="https://example.invalid/megacorp-annual-report.pdf",
            title="MegaCorp Annual Report 2025",
        ),
    ],
    observed_at="2026-01-15T10:00:00Z",
)
proof_a.id = proof_id(proof_a)

# 2. Claim B: Investigative report disputes revenue figure
claim_b = Claim(
    subject="MegaCorp",
    predicate="reported_revenue",
    object="USD 30 million",
)
proof_b = Proof(
    claim=claim_b,
    evidence=[
        Evidence(
            type="web",
            source="https://example.invalid/investigative-report",
            title="MegaCorp Revenue Discrepancy Investigation",
        ),
    ],
    observed_at="2026-03-20T14:00:00Z",
    status="CONTESTED",
)
proof_b.id = proof_id(proof_b)

# 3. Create the graph relationship
graph = ProofGraph()
graph.add(ProofRelation(
    source_id=proof_b.id,
    target_id=proof_a.id,
    relation=Relation.CONTRADICTS,
    metadata={"reason": "Investigative report found inflated figures"},
))

# 4. Also add a corroborating claim
claim_c = Claim(
    subject="MegaCorp",
    predicate="reported_revenue",
    object="USD 30 million",
)
proof_c = Proof(
    claim=claim_c,
    evidence=[
        Evidence(
            type="api",
            source="https://example.invalid/sec-filings/megacorp",
            title="SEC Filing Data",
        ),
    ],
    observed_at="2026-04-01T09:00:00Z",
)
proof_c.id = proof_id(proof_c)

graph.add(ProofRelation(
    source_id=proof_c.id,
    target_id=proof_b.id,
    relation=Relation.CORROBORATES,
))

# 5. Query the graph
print("=== PROOF Records ===\n")
for label, p in [("Claim A", proof_a), ("Claim B", proof_b), ("Claim C", proof_c)]:
    print(f"{label}: {p.claim.subject} {p.claim.predicate} {p.claim.object}")
    print(f"  ID: {p.id}")
    print(f"  Status: {p.status}\n")

print("=== Graph Relationships ===\n")
print(json.dumps(graph.to_dict(), indent=2))

print("\n=== Contradictions for Claim A ===\n")
contradictions = graph.contradictions(proof_a.id)
for c in contradictions:
    print(f"  {c.source_id} --contradicts--> {c.target_id}")

print("\n=== Supporters for Claim B ===\n")
supporters = graph.supporters(proof_b.id)
for s in supporters:
    print(f"  {s.source_id} --{s.relation}--> {s.target_id}")
