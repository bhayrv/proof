# PROOF Protocol Test Vectors

This directory contains authoritative JSON test vectors for the PROOF Protocol (v0.2).

To claim compliance with the PROOF Protocol, an independent implementation MUST pass all test vectors in this directory.

## Available Vectors

- **`canonicalization.json`**: Tests the PROOF Constrained Canonical JSON Profile. Ensures identical byte-for-byte serialization across implementations, covering Unicode sorting, control characters, escaping, and numeric constraints.
- **`identity.json`**: Tests the SHA-256 identity computation. Ensures implementations correctly isolate the immutable payload (stripping mutable lifecycle/attestation fields) before hashing.
- **`attestation.json`**: Tests Ed25519 cryptographic signing and verification over the canonicalized identity payload.

## Usage

Each file contains a JSON array of test cases. A standard test case format includes:

- `description`: Human-readable description of the test scenario.
- `input`: The input data (typically a JSON object or string).
- `expected`: The expected output (e.g., canonical bytes, hash string, or verification boolean).

For an example of how to execute these vectors against an implementation, see the Python test suite in the root `tests/` directory.

## Goal

These vectors exist to guarantee **deterministic, bit-for-bit interoperability** across languages (Python, JavaScript, Rust, Go, etc.) without relying on a central authority or a single reference codebase.
