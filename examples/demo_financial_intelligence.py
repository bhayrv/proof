#!/usr/bin/env python3
"""
PROOF Protocol - Financial Intelligence Demonstration
This demonstration treats PROOF as a first-class proof-of-concept for a financial data pipeline.

Scenario:
1. An intelligence pipeline extracts a claim from an SEC filing (synthetic).
2. The pipeline associates the claim with evidence (the source URL).
3. A reviewer (or system) attests to the claim.
4. Later, an amended filing contradicts the original claim. Both claims coexist in the PROOF graph.
"""

import json
from proof import (
    Claim, Evidence, Proof, Status, Relation,
    proof_id, create_attestation, verify_proof
)

def main():
    print("==================================================")
    print("PROOF DEMO: FINANCIAL INTELLIGENCE")
    print("==================================================")
    
    # ---------------------------------------------------------
    # 1. INITIAL REPORTED CLAIM
    # ---------------------------------------------------------
    print("\n[1] Extracting synthetic initial earnings claim...")
    claim_initial = Claim(
        subject="Acme Corp (Synthetic)",
        predicate="reported_net_income",
        object="USD 42,000,000"
    )

    evidence_initial = Evidence(
        type="document",
        source="https://sec.example.invalid/archives/edgar/data/0000000000/0000000000-26-000001.txt",
        title="Form 10-K (Synthetic)"
    )

    proof_initial = Proof(
        claim=claim_initial,
        evidence=[evidence_initial],
        status=Status.OBSERVED
    )
    proof_initial.id = proof_id(proof_initial)

    print(f"Generated Identity (SHA-256): {proof_initial.id}")

    # ---------------------------------------------------------
    # 2. ATTESTATION
    # ---------------------------------------------------------
    print("\n[2] Analyst verifies extraction and signs the record...")
    attestation, private_key = create_attestation(proof_initial)
    proof_initial.attestations.append(attestation.to_dict())

    # ---------------------------------------------------------
    # 3. VERIFICATION
    # ---------------------------------------------------------
    print("\n[3] Independent verification of the signed claim...")
    result = verify_proof(proof_initial, attestations=[attestation])
    print(f"Verification Successful: {result.ok}")

    # ---------------------------------------------------------
    # 4. CONTRADICTION (AMENDED FILING)
    # ---------------------------------------------------------
    print("\n[4] A week later, an amended 10-K/A is filed with revised figures.")
    claim_amended = Claim(
        subject="Acme Corp (Synthetic)",
        predicate="reported_net_income",
        object="USD 38,000,000"
    )
    evidence_amended = Evidence(
        type="document",
        source="https://sec.example.invalid/archives/edgar/data/0000000000/0000000000-26-000002.txt",
        title="Form 10-K/A (Synthetic Amendment)"
    )

    proof_amended = Proof(
        claim=claim_amended,
        evidence=[evidence_amended],
        status=Status.OBSERVED
    )
    proof_amended.id = proof_id(proof_amended)
    
    # Sign the amended proof
    att_amended, _ = create_attestation(proof_amended)
    proof_amended.attestations.append(att_amended.to_dict())

    # ---------------------------------------------------------
    # 5. GRAPH RELATIONSHIP
    # ---------------------------------------------------------
    print("\n[5] Linking the contradiction in the graph...")
    print("PROOF preserves BOTH claims. It does not silently overwrite history.")
    
    # Represent the contradiction in a conceptual graph format
    graph_edge = {
        "source": proof_amended.id,
        "relation": Relation.CONTRADICTS.value,
        "target": proof_initial.id,
        "metadata": {"note": "10-K/A revises net income downward"}
    }
    
    # Also update the lifecycle status of the initial proof
    proof_initial.status = Status.CONTESTED
    
    print(f"\nRelationship established: {proof_amended.id[:12]}... --CONTRADICTS--> {proof_initial.id[:12]}...")
    print(f"Initial Claim Status: {proof_initial.status.value}")
    
    print("\n[6] Final Records (JSON):")
    print("--- Initial (Contested) ---")
    print(json.dumps(proof_initial.to_dict(), indent=2))
    print("\n--- Amended ---")
    print(json.dumps(proof_amended.to_dict(), indent=2))
    print("\n--- Graph Edge ---")
    print(json.dumps(graph_edge, indent=2))
    
if __name__ == "__main__":
    main()
