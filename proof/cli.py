"""
PROOF Protocol — Command-Line Interface

Commands:
    proof create    Create a PROOF record
    proof inspect   Display a PROOF record's contents
    proof identity  Compute content identity
    proof keygen    Generate a new Ed25519 private key
    proof sign      Sign a PROOF record
    proof verify    Verify a PROOF record

All commands support JSON input/output for pipeline compatibility.

Usage examples:

    # Create a claim
    proof create --subject "Acme" --predicate "raised" --object "USD 40M"

    # Create with evidence
    proof create --subject "Acme" --predicate "raised" --object "USD 40M" \\
        --evidence-type web --evidence-source "https://example.com/funding"

    # Pipe JSON through identity and signing
    proof create ... | proof identity | proof sign

    # Verify a PROOF record
    cat record.json | proof verify

See README.md for more examples.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from .attestation import Attestation, create_attestation, verify_attestation
from .evidence import Evidence
from .identity import proof_id
from .lifecycle import Status
from .models import Claim, Proof
from .verify import VerificationResult, verify_proof


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the ``proof`` CLI."""
    parser = argparse.ArgumentParser(
        prog="proof",
        description="PROOF Protocol — local CLI for claims, evidence, and verification",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # -- proof create -------------------------------------------------- #
    create_parser = subparsers.add_parser(
        "create",
        help="Create a PROOF record",
    )
    create_parser.add_argument("--subject", required=True, help="Claim subject")
    create_parser.add_argument("--predicate", required=True, help="Claim predicate")
    create_parser.add_argument("--object", required=True, help="Claim object (string or JSON value)")
    create_parser.add_argument("--evidence-type", help="Evidence type")
    create_parser.add_argument("--evidence-source", help="Evidence source URI")
    create_parser.add_argument("--evidence-title", help="Evidence title")
    create_parser.add_argument("--observed-at", help="ISO 8601 observation timestamp")
    create_parser.add_argument("--status", default="OBSERVED", help="Lifecycle status (default: OBSERVED)")

    # -- proof inspect ------------------------------------------------- #
    subparsers.add_parser(
        "inspect",
        help="Display a PROOF record from JSON stdin",
    )

    # -- proof identity ------------------------------------------------ #
    subparsers.add_parser(
        "identity",
        help="Compute and display content identity from JSON stdin",
    )

    # -- proof keygen -------------------------------------------------- #
    subparsers.add_parser(
        "keygen",
        help="Generate a new Ed25519 private key and output as JSON",
    )

    # -- proof sign ---------------------------------------------------- #
    sign_parser = subparsers.add_parser(
        "sign",
        help="Sign a PROOF record (reads JSON from stdin)",
    )
    sign_parser.add_argument(
        "--private-key",
        help="Hex-encoded Ed25519 private key (64 hex characters). "
             "Can also be provided via PROOF_PRIVATE_KEY env var.",
    )
    sign_parser.add_argument(
        "--created-at",
        help="ISO 8601 timestamp for the attestation",
    )

    # -- proof verify -------------------------------------------------- #
    subparsers.add_parser(
        "verify",
        help="Verify a PROOF record (reads JSON from stdin)",
    )

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    try:
        if args.command == "create":
            return _cmd_create(args)
        elif args.command == "inspect":
            return _cmd_inspect()
        elif args.command == "identity":
            return _cmd_identity()
        elif args.command == "keygen":
            return _cmd_keygen()
        elif args.command == "sign":
            return _cmd_sign(args)
        elif args.command == "verify":
            return _cmd_verify()
        else:
            parser.print_help()
            return 1
    except Exception as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1


# -------------------------------------------------------------------- #
#  Command implementations
# -------------------------------------------------------------------- #

def _cmd_create(args: argparse.Namespace) -> int:
    """Create a new PROOF record and print it as JSON."""
    # Try to parse object as JSON value; fall back to string
    try:
        obj_value = json.loads(args.object)
    except (json.JSONDecodeError, TypeError):
        obj_value = args.object

    claim = Claim(
        subject=args.subject,
        predicate=args.predicate,
        object=obj_value,
    )

    evidence_list: list[Evidence] = []
    if args.evidence_type and args.evidence_source:
        evidence_list.append(Evidence(
            type=args.evidence_type,
            source=args.evidence_source,
            title=args.evidence_title,
        ))

    # Validate status
    try:
        status = Status(args.status)
    except ValueError:
        valid = ", ".join(s.value for s in Status)
        print(
            json.dumps({"error": f"Invalid status: {args.status}. Valid: {valid}"}),
            file=sys.stderr,
        )
        return 1

    proof = Proof(
        claim=claim,
        evidence=evidence_list,
        observed_at=args.observed_at,
        status=status.value,
    )

    # Compute and attach identity
    proof.id = proof_id(proof)

    print(json.dumps(proof.to_dict(), indent=2))
    return 0


def _cmd_inspect() -> int:
    """Read a PROOF JSON from stdin and pretty-print it."""
    data = json.load(sys.stdin)
    print(json.dumps(data, indent=2))
    return 0


def _cmd_identity() -> int:
    """Compute identity from JSON stdin and output the record with id."""
    data = json.load(sys.stdin)
    proof = _dict_to_proof(data)
    computed_id = proof_id(proof)
    data["id"] = computed_id
    print(json.dumps(data, indent=2))
    return 0


def _cmd_keygen() -> int:
    """Generate a new Ed25519 private key and output as JSON."""
    from .crypto import generate_private_key, private_key_bytes, public_key_bytes

    key = generate_private_key()
    priv_hex = private_key_bytes(key).hex()
    pub_hex = public_key_bytes(key).hex()

    print(json.dumps({
        "private_key": priv_hex,
        "public_key": pub_hex,
    }, indent=2))
    return 0


def _cmd_sign(args: argparse.Namespace) -> int:
    """Sign a PROOF record from stdin and output with attestation."""
    import os
    from .crypto import load_private_key

    # Attempt to read key from args or environment
    key_hex = args.private_key or os.environ.get("PROOF_PRIVATE_KEY")
    if not key_hex:
        print(
            json.dumps({"error": "Missing private key. Provide via --private-key or PROOF_PRIVATE_KEY env var."}),
            file=sys.stderr,
        )
        return 1

    try:
        key_bytes = bytes.fromhex(key_hex)
        private_key = load_private_key(key_bytes)
    except Exception as e:
        print(json.dumps({"error": f"Invalid private key: {e}"}), file=sys.stderr)
        return 1

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON on stdin: {e}"}), file=sys.stderr)
        return 1

    proof = _dict_to_proof(data)

    attestation, _ = create_attestation(
        proof,
        private_key=private_key,
        created_at=args.created_at,
    )

    # Add attestation to the record
    if "attestations" not in data:
        data["attestations"] = []
    data["attestations"].append(attestation.to_dict())

    # Ensure identity is set
    if "id" not in data or data["id"] is None:
        data["id"] = proof_id(proof)

    print(json.dumps(data, indent=2))

    return 0


def _cmd_verify() -> int:
    """Verify a PROOF record from stdin."""
    data = json.load(sys.stdin)
    proof = _dict_to_proof(data)

    # Reconstruct attestations
    att_list: list[Attestation] = []
    for att_data in data.get("attestations", []):
        att_list.append(Attestation(
            proof_id=att_data["proof_id"],
            algorithm=att_data["algorithm"],
            public_key=att_data["public_key"],
            signature=att_data["signature"],
            created_at=att_data.get("created_at"),
        ))

    result = verify_proof(proof, attestations=att_list if att_list else None)
    print(json.dumps(result.to_dict(), indent=2))
    return 0 if result.ok else 1


# -------------------------------------------------------------------- #
#  Helpers
# -------------------------------------------------------------------- #

def _dict_to_proof(data: dict) -> Proof:
    """Reconstruct a Proof object from a dictionary."""
    claim_data = data.get("claim", {})
    claim = Claim(
        subject=claim_data.get("subject", ""),
        predicate=claim_data.get("predicate", ""),
        object=claim_data.get("object"),
    )

    evidence_list: list[Evidence] = []
    for ev in data.get("evidence", []):
        evidence_list.append(Evidence(
            type=ev.get("type", ""),
            source=ev.get("source", ""),
            title=ev.get("title"),
            content_hash=ev.get("content_hash"),
            observed_at=ev.get("observed_at"),
            metadata=ev.get("metadata"),
        ))

    return Proof(
        claim=claim,
        evidence=evidence_list,
        attestations=data.get("attestations", []),
        observed_at=data.get("observed_at"),
        status=data.get("status", "OBSERVED"),
        id=data.get("id"),
    )


if __name__ == "__main__":
    sys.exit(main())
