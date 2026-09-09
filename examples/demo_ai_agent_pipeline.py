#!/usr/bin/env python3
"""
PROOF Protocol - AI Agent Pipeline Demonstration (Flagship Demo)

This represents the flagship value proposition of PROOF for AI systems:
AI extraction is inherently probabilistic. PROOF provides a deterministic wrapper 
so downstream systems can mathematically verify the exact provenance and evidence 
without trusting the AI's internal "hallucination-free" claims.

Workflow:
[Source Text] -> [AI Extraction (Mock)] -> [Evidence Binding] -> [Human/System Review] 
-> [Cryptographic Attestation] -> [PROOF Object] -> [Deterministic Verification]
"""

import json
from proof import (
    Claim, Evidence, Proof, Status,
    proof_id, create_attestation, verify_proof
)

def mock_ai_extraction(text: str) -> dict:
    """
    Simulates a Large Language Model extracting structured triples from unstructured text.
    In the real world, this step is probabilistic and could hallucinate.
    """
    # Simulated "prompt": Extract subject, predicate, object from the text.
    if "QuantumCompute Corp achieved quantum supremacy" in text:
        return {
            "subject": "QuantumCompute Corp",
            "predicate": "achieved",
            "object": "quantum supremacy"
        }
    return {}

def main():
    print("==================================================")
    print("PROOF DEMO: AI AGENT PIPELINE")
    print("==================================================")

    # ---------------------------------------------------------
    # 1. SOURCE INGESTION
    # ---------------------------------------------------------
    source_url = "https://news.example.invalid/quantum-breakthrough"
    source_text = "In a stunning announcement today, QuantumCompute Corp achieved quantum supremacy using their new 1024-qubit processor."
    print(f"\n[1] Ingesting Source...")
    print(f"URL: {source_url}")
    print(f"Text: '{source_text}'")

    # ---------------------------------------------------------
    # 2. AI EXTRACTION (PROBABILISTIC)
    # ---------------------------------------------------------
    print("\n[2] Running AI Extraction (Probabilistic)...")
    extracted_data = mock_ai_extraction(source_text)
    print(f"Extracted Claim: {extracted_data}")

    # ---------------------------------------------------------
    # 3. EVIDENCE ASSOCIATION
    # ---------------------------------------------------------
    print("\n[3] Binding extracted claim to its evidence...")
    claim = Claim(**extracted_data)
    evidence = Evidence(
        type="article",
        source=source_url,
        title="Quantum Breakthrough News"
    )

    proof = Proof(claim=claim, evidence=[evidence], status=Status.UNKNOWN)
    proof.id = proof_id(proof)
    print(f"Generated Deterministic Identity: {proof.id}")

    # ---------------------------------------------------------
    # 4. REVIEW & ATTESTATION
    # ---------------------------------------------------------
    print("\n[4] System/Human Review & Cryptographic Attestation...")
    print("A reviewing agent (or human) verifies the extraction matches the source.")
    print("The reviewer signs the immutable PROOF identity.")
    
    # The signature explicitly covers the exact claim + the exact evidence.
    # It does NOT assert universal truth, but rather "I extracted this from that."
    attestation, private_key = create_attestation(proof)
    proof.attestations.append(attestation.to_dict())
    proof.status = Status.OBSERVED
    print(f"Signature attached by reviewer.")

    # ---------------------------------------------------------
    # 5. DETERMINISTIC VERIFICATION
    # ---------------------------------------------------------
    print("\n[5] Downstream Verification (Deterministic)...")
    print("A completely separate system receives the JSON payload.")
    
    result = verify_proof(proof, attestations=[attestation])
    print("Verification Result:")
    print(json.dumps(result.to_dict(), indent=2))
    
    if result.ok:
        print("\nSUCCESS: The downstream system mathematically verified the PROOF record.")
        print("It can verify the claimed provenance and attestation integrity without trusting the AI model itself.")
    else:
        print("\nFAILURE: The record is invalid.")

if __name__ == "__main__":
    main()
