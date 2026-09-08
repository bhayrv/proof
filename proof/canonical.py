"""
PROOF Protocol — Canonicalization

Canonicalization converts a PROOF object into one deterministic
JSON representation.

The same logical object must always produce the same bytes.
Those bytes can then be hashed and signed.
"""

import json
from typing import Any


def canonicalize(data: Any) -> bytes:
    """
    Convert JSON-compatible data into deterministic UTF-8 bytes.

    Rules:
    - Keys are sorted.
    - Whitespace is removed.
    - Unicode is preserved.
    - UTF-8 encoding is used.
    """

    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")