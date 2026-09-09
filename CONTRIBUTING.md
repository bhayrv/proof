# Contributing to PROOF Protocol

Thank you for your interest in contributing to PROOF! 

We welcome contributions of all kinds, including bug reports, feature requests, documentation improvements, and code contributions.

## Principles

1. **Protocol Stability**: PROOF 0.2 is an experimental release but aims for backwards compatibility wherever possible. Breaking changes to the core identity or canonicalization specifications must be carefully considered and typically require a version bump.
2. **Deterministic By Design**: Any changes to `proof/canonical.py` or `proof/identity.py` MUST be accompanied by corresponding updates to the authoritative test vectors in `spec/test-vectors/`.
3. **Simplicity**: PROOF avoids the complexity of tokens, blockchains, or heavy external dependencies. Please keep enhancements focused and minimal.

## Development Setup

1. Clone the repository.
2. We recommend using a Python virtual environment.
3. Install the package in editable mode with development dependencies:

```bash
pip install -e .[dev]
```

## Testing

PROOF maintains a rigorous test suite. Before submitting a pull request, please ensure all tests pass:

```bash
python -m pytest -v
```

If you are modifying the canonicalization or identity specification, you MUST also verify that the independent JavaScript implementation correctly processes the test vectors:

```bash
node implementations/javascript/test.js
```

## Test Vectors

The PROOF test vectors in `spec/test-vectors/` are the absolute source of truth for interoperability. 
If you add a new edge case or clarify the specification, please add a new test vector to the corresponding JSON file.

## Pull Request Process

1. Fork the repo and create your branch from `main`.
2. Ensure your code follows the style of the existing project.
3. Add tests for any new logic.
4. Update documentation if necessary.
5. Open a Pull Request! We will review it as soon as possible.
