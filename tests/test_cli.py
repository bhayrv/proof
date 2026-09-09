"""
PROOF Protocol — CLI Tests

Smoke tests for the proof CLI commands.
"""

import json
import os
import subprocess

import pytest

from proof.cli import main


class TestCLICreate:
    """Tests for the 'proof create' command."""

    def test_create_basic(self, capsys):
        exit_code = main([
            "create",
            "--subject", "TestCo",
            "--predicate", "announced",
            "--object", "something",
        ])
        assert exit_code == 0
        captured = capsys.readouterr()
        assert captured.err == ""
        data = json.loads(captured.out)
        assert data["proof"] == "0.2"
        assert data["claim"]["subject"] == "TestCo"
        assert data["id"] is not None
        assert data["id"].startswith("sha256:")

    def test_create_with_evidence(self, capsys):
        exit_code = main([
            "create",
            "--subject", "TestCo",
            "--predicate", "reported",
            "--object", "results",
            "--evidence-type", "web",
            "--evidence-source", "https://example.invalid/report",
            "--evidence-title", "Test Report",
        ])
        assert exit_code == 0
        data = json.loads(capsys.readouterr().out)
        assert len(data["evidence"]) == 1
        assert data["evidence"][0]["type"] == "web"

    def test_create_with_json_object(self, capsys):
        exit_code = main([
            "create",
            "--subject", "TestCo",
            "--predicate", "reported",
            "--object", '{"revenue": 1000000}',
        ])
        assert exit_code == 0
        data = json.loads(capsys.readouterr().out)
        assert data["claim"]["object"] == {"revenue": 1000000}

    def test_create_with_status(self, capsys):
        exit_code = main([
            "create",
            "--subject", "X",
            "--predicate", "is",
            "--object", "Y",
            "--status", "VERIFIED",
        ])
        assert exit_code == 0
        data = json.loads(capsys.readouterr().out)
        assert data["status"] == "VERIFIED"

    def test_create_invalid_status(self, capsys):
        exit_code = main([
            "create",
            "--subject", "X",
            "--predicate", "is",
            "--object", "Y",
            "--status", "INVALID",
        ])
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Invalid status" in captured.err


class TestCLIIdentity:
    """Tests for the 'proof identity' command."""

    def test_identity_from_stdin(self, monkeypatch, capsys):
        import io
        record = json.dumps({
            "proof": "0.2",
            "claim": {"subject": "X", "predicate": "is", "object": "Y"},
            "evidence": [],
            "status": "OBSERVED",
        })
        monkeypatch.setattr("sys.stdin", io.StringIO(record))
        exit_code = main(["identity"])
        assert exit_code == 0
        captured = capsys.readouterr()
        assert captured.err == ""
        data = json.loads(captured.out)
        assert data["id"].startswith("sha256:")


class TestCLIInspect:
    """Tests for the 'proof inspect' command."""

    def test_inspect_from_stdin(self, monkeypatch, capsys):
        import io
        record = json.dumps({"proof": "0.2", "claim": {"subject": "X"}})
        monkeypatch.setattr("sys.stdin", io.StringIO(record))
        exit_code = main(["inspect"])
        assert exit_code == 0
        data = json.loads(capsys.readouterr().out)
        assert data["proof"] == "0.2"


class TestCLIVerify:
    """Tests for the 'proof verify' command."""

    def test_verify_unsigned_record(self, monkeypatch, capsys):
        import io
        from proof import Claim, Evidence, Proof, proof_id

        proof = Proof(
            claim=Claim("X", "is", "Y"),
            evidence=[Evidence(type="web", source="https://example.invalid")],
        )
        proof.id = proof_id(proof)
        record = json.dumps(proof.to_dict())
        monkeypatch.setattr("sys.stdin", io.StringIO(record))
        # Unsigned records should still verify identity
        exit_code = main(["verify"])
        captured = capsys.readouterr()
        assert captured.err == ""
        data = json.loads(captured.out)
        assert data["identity_valid"] is True
        assert data["signature_valid"] is False


class TestCLIHelp:
    """Tests for the help output."""

    def test_no_args(self, capsys):
        exit_code = main([])
        assert exit_code == 0


class TestCLIPipeline:
    """Tests for end-to-end pipeline semantics and stdout/stderr separation."""

    def test_missing_signing_key_fails(self, monkeypatch, capsys):
        """proof sign MUST fail cleanly if no key is provided."""
        import io
        record = json.dumps({
            "proof": "0.2",
            "claim": {"subject": "X", "predicate": "is", "object": "Y"},
            "evidence": [],
            "status": "OBSERVED"
        })
        monkeypatch.setattr("sys.stdin", io.StringIO(record))
        if "PROOF_PRIVATE_KEY" in os.environ:
            monkeypatch.delenv("PROOF_PRIVATE_KEY")

        exit_code = main(["sign"])
        assert exit_code != 0
        captured = capsys.readouterr()
        assert captured.out == ""
        assert "Missing private key" in captured.err

    def test_keygen_creates_valid_keys(self, capsys):
        """proof keygen should output a valid keypair."""
        exit_code = main(["keygen"])
        assert exit_code == 0
        captured = capsys.readouterr()
        assert captured.err == ""
        keys = json.loads(captured.out)
        assert "private_key" in keys
        assert "public_key" in keys
        assert len(keys["private_key"]) == 64
        assert len(keys["public_key"]) == 64

    def test_end_to_end_pipeline(self, monkeypatch):
        """Test create | sign | verify as subprocesses to strictly validate standard streams."""
        # Step 1: Keygen
        keygen_proc = subprocess.run(
            ["python", "-m", "proof", "keygen"],
            capture_output=True, text=True, check=True
        )
        keys = json.loads(keygen_proc.stdout)
        priv_key = keys["private_key"]
        
        # Step 2: Create
        create_proc = subprocess.run(
            [
                "python", "-m", "proof", "create",
                "--subject", "Acme",
                "--predicate", "raised",
                "--object", "USD 40M",
                "--evidence-type", "web",
                "--evidence-source", "https://example.com"
            ],
            capture_output=True, text=True, check=True
        )
        assert create_proc.stderr == ""
        
        # Step 3: Sign (via stdin)
        env = os.environ.copy()
        env["PROOF_PRIVATE_KEY"] = priv_key
        sign_proc = subprocess.run(
            ["python", "-m", "proof", "sign"],
            input=create_proc.stdout,
            capture_output=True, text=True, check=True,
            env=env
        )
        assert sign_proc.stderr == ""
        signed_record = json.loads(sign_proc.stdout)
        assert len(signed_record["attestations"]) == 1

        # Step 4: Verify (via stdin)
        verify_proc = subprocess.run(
            ["python", "-m", "proof", "verify"],
            input=sign_proc.stdout,
            capture_output=True, text=True, check=True
        )
        assert verify_proc.stderr == ""
        result = json.loads(verify_proc.stdout)
        assert result["identity_valid"] is True
        assert result["signature_valid"] is True
        assert len(result["errors"]) == 0
