#!/usr/bin/env python3
"""
PROOF Protocol - Temporal Change / Supersession Demonstration

Scenario:
1. Claim A: Company X acquired Company Y for $500M.
2. Claim B: The transaction value was revised to $420M.
3. Claim B --supersedes--> Claim A.

Key Takeaway:
PROOF does not automatically decide the "current truth" or delete the past. 
It preserves the lineage so a consumer's policy can determine interpretation.
"""

import json
from proof import (
    Claim, Evidence, Proof, Status, Relation,
    proof_id, create_attestation, verify_proof
)

def main():
    print("==================================================")
    print("PROOF DEMO: TEMPORAL SUPERSESSION")
    print("==================================================")

    # ---------------------------------------------------------
    # 1. INITIAL CLAIM (A)
    # ---------------------------------------------------------
    print("\n[1] Creating initial acquisition claim (A)...")
    claim_a = Claim(
        subject="Company X",
        predicate="acquired_company_y_for",
        object="USD 500,000,000"
    )
    evidence_a = Evidence(
        type="press_release",
        source="https://press.example.invalid/acquisition-announcement",
        title="Initial Acquisition Announcement"
    )
    proof_a = Proof(claim=claim_a, evidence=[evidence_a], status=Status.VERIFIED)
    proof_a.id = proof_id(proof_a)

    print(f"Proof A Identity: {proof_a.id}")

    # ---------------------------------------------------------
    # 2. REVISED CLAIM (B)
    # ---------------------------------------------------------
    print("\n[2] Creating revised acquisition claim (B)...")
    claim_b = Claim(
        subject="Company X",
        predicate="acquired_company_y_for",
        object="USD 420,000,000"
    )
    evidence_b = Evidence(
        type="press_release",
        source="https://press.example.invalid/acquisition-revised",
        title="Revised Acquisition Terms"
    )
    proof_b = Proof(claim=claim_b, evidence=[evidence_b], status=Status.VERIFIED)
    proof_b.id = proof_id(proof_b)

    print(f"Proof B Identity: {proof_b.id}")

    # ---------------------------------------------------------
    # 3. SUPERSESSION RELATIONSHIP
    # ---------------------------------------------------------
    print("\n[3] Establishing the lineage...")
    # Update the lifecycle of the old claim
    proof_a.status = Status.SUPERSEDED
    
    # Establish the graph edge representing the replacement
    graph_edge = {
        "source": proof_b.id,
        "relation": Relation.SUPERSEDES.value,
        "target": proof_a.id,
        "metadata": {"note": "Terms revised prior to closing"}
    }

    print(f"\nRelationship: {proof_b.id[:12]}... --SUPERSEDES--> {proof_a.id[:12]}...")
    
    print("\n[4] Why does this matter?")
    print("PROOF preserves the historical lineage. It does NOT automatically assert")
    print("that Claim B is the definitive 'truth'. A consuming machine/application")
    print("applies its own policy to interpret the 'supersedes' relation to determine")
    print("the active state.")
    
    print("\n--- Final Graph State (JSON) ---")
    print(json.dumps({
        "records": [proof_a.to_dict(), proof_b.to_dict()],
        "edges": [graph_edge]
    }, indent=2))

if __name__ == "__main__":
    main()
