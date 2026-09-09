"""
PROOF Protocol — Canonicalization

Converts a PROOF data structure into one deterministic JSON byte
sequence. The same logical object always produces the same bytes,
which can then be hashed or signed.

Canonicalization rules (PROOF 0.2 Constrained Canonical JSON Profile):

    1. Encoding:  UTF-8, no BOM.
    2. Whitespace: No insignificant whitespace between tokens. Separators are "," and ":".
    3. Key ordering: Lexicographic sort by Unicode code point.
    4. Strings: Double-quoted. Escaped strictly: \", \\, \\b, \\f, \\n, \\r, \\t,
       and control characters U+0000–U+001F via \\uXXXX (lowercase hex).
       Non-ASCII and all characters >= U+0020 are emitted directly as UTF-8.
    5. Numbers: Integers only within the safe range
       [-(2**53 - 1), 2**53 - 1]. No leading zeros (except exactly 0),
       no decimal point, no exponent notation.
    6. Booleans: true / false (lowercase).
    7. Null: null (lowercase).
    8. Arrays: Ordered, elements serialized in order.

This profile is inspired by generic deterministic JSON canonicalization efforts
but explicitly rejects complex floating-point serialization rules. It does not
claim generic conformance to RFC 8785.

Cross-language reproducibility:

    Python: json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

See spec/PROOF.md §4.4 for the normative specification.
"""

from __future__ import annotations

import json
from typing import Any

# Safe integer range for cross-language interoperability.
# Corresponds to IEEE 754 double-precision exact integer representation
# and JavaScript's Number.MAX_SAFE_INTEGER.
SAFE_INTEGER_MIN: int = -(2**53 - 1)  # -9007199254740991
SAFE_INTEGER_MAX: int = 2**53 - 1      #  9007199254740991


def canonicalize(data: Any) -> bytes:
    """Convert JSON-compatible data into deterministic UTF-8 bytes.

    Parameters
    ----------
    data
        A JSON-serializable Python object.  All values that participate
        in identity computation MUST conform to the interoperable type
        restrictions defined in spec/PROOF.md §4.3.

    Returns
    -------
    bytes
        The canonical UTF-8 byte sequence.

    Raises
    ------
    ValueError
        If *data* contains a float (including NaN / Infinity) or an
        integer outside the safe range.
    TypeError
        If *data* is not JSON-serializable.
    """
    _validate_types(data)
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _validate_types(data: Any, path: str = "$") -> None:
    """Recursively validate that *data* contains only interoperable types."""
    if data is None or isinstance(data, (bool, str)):
        return
    if isinstance(data, int):
        if not (SAFE_INTEGER_MIN <= data <= SAFE_INTEGER_MAX):
            raise ValueError(
                f"Integer at {path} is outside the safe interoperable "
                f"range [{SAFE_INTEGER_MIN}, {SAFE_INTEGER_MAX}]: {data}"
            )
        return
    if isinstance(data, float):
        raise ValueError(
            f"Floating-point value at {path} is not allowed in "
            f"identity-participating fields: {data!r}"
        )
    if isinstance(data, list):
        for i, item in enumerate(data):
            _validate_types(item, f"{path}[{i}]")
        return
    if isinstance(data, dict):
        for key in data:
            if not isinstance(key, str):
                raise ValueError(
                    f"Non-string key at {path}: {key!r}"
                )
            _validate_types(data[key], f"{path}.{key}")
        return
    raise TypeError(
        f"Unsupported type at {path}: {type(data).__name__}"
    )