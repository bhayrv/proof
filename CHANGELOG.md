# Changelog

All notable changes to the PROOF Protocol will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-09-09

### Added
- **PROOF Constrained Canonical JSON Profile**: A deterministic, subset JSON canonicalization profile specifically engineered to ban floating-point values and strictly define Unicode escaping.
- Authoritative Test Vectors for Canonicalization, Identity, and Attestation.
- Complete Python Reference Implementation (100% test coverage).
- Complete Independent JavaScript Implementation (Identity & Canonicalization).
- Visualizer HTML demo (`examples/visualizer/index.html`).
- E2E PowerShell CLI workflow (`examples/cli_end_to_end.ps1`).
- Multiple advanced demonstrations: Financial Intelligence, Temporal Supersession, and AI Agent Pipeline.
- GitHub Actions CI workflow for Python and JavaScript suites.

### Changed
- Replaced the vague RFC 8785 claim with the bespoke, safer PROOF Constrained Canonical JSON Profile.
- Improved error handling and edge-case resilience in the CLI tool.
- Protocol version field introduced as `"proof": "0.2"` in the payload structure.
- Identity generation logic now strictly excludes mutable lifecycle properties (`status`, `observed_at`, `attestations`).

### Removed
- Support for floating-point values in the JSON identity payload. Values outside the safe integer range or with decimals must now be represented as strings to guarantee cross-language interoperability.

## [0.1.0] - Pre-release Prototype

### Added
- Initial conceptual prototype of the PROOF data model.
- Basic SHA-256 identity mapping.
- Prototype cryptographic signing logic.
