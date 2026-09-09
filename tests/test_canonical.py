"""
PROOF Protocol — Canonicalization Tests

Tests the canonical JSON serialization defined in spec/PROOF.md §4.4.
"""

import pytest

from proof.canonical import (
    SAFE_INTEGER_MAX,
    SAFE_INTEGER_MIN,
    canonicalize,
)


class TestCanonicalKeyOrdering:
    """Object keys must be sorted lexicographically."""

    def test_simple_sort(self):
        result = canonicalize({"b": 2, "a": 1})
        assert result == b'{"a":1,"b":2}'

    def test_nested_sort(self):
        result = canonicalize({"a": {"z": 1, "a": 2}})
        assert result == b'{"a":{"a":2,"z":1}}'

    def test_deeply_nested(self):
        data = {"c": {"b": {"a": 1}}}
        result = canonicalize(data)
        assert result == b'{"c":{"b":{"a":1}}}'

    def test_supplementary_sort(self):
        # 💡 is U+1F4A1, 💩 is U+1F4A9, a is U+0061
        result = canonicalize({"💩": 2, "a": 1, "💡": 3})
        # Order should be 'a', then '💡', then '💩'
        assert result == '{"a":1,"💡":3,"💩":2}'.encode("utf-8")


class TestCanonicalTypes:
    """All interoperable types serialize correctly."""

    def test_string(self):
        assert canonicalize("hello") == b'"hello"'

    def test_integer(self):
        assert canonicalize(42) == b"42"

    def test_negative_integer(self):
        assert canonicalize(-100) == b"-100"

    def test_zero(self):
        assert canonicalize(0) == b"0"

    def test_true(self):
        assert canonicalize(True) == b"true"

    def test_false(self):
        assert canonicalize(False) == b"false"

    def test_null(self):
        assert canonicalize(None) == b"null"

    def test_empty_object(self):
        assert canonicalize({}) == b"{}"

    def test_empty_array(self):
        assert canonicalize([]) == b"[]"

    def test_empty_string(self):
        assert canonicalize("") == b'""'


class TestCanonicalArrays:
    """Arrays preserve element order."""

    def test_order_preserved(self):
        assert canonicalize([3, 1, 2]) == b"[3,1,2]"

    def test_nested_arrays(self):
        assert canonicalize([[1, 2], [3, 4]]) == b"[[1,2],[3,4]]"

    def test_mixed_types(self):
        result = canonicalize([1, "two", True, None])
        assert result == b'[1,"two",true,null]'


class TestCanonicalUnicode:
    """Non-ASCII characters are preserved as UTF-8."""

    def test_accented(self):
        result = canonicalize({"text": "café"})
        assert result == '{"text":"café"}'.encode("utf-8")

    def test_emoji(self):
        result = canonicalize({"icon": "\U0001f512"})
        assert result == '{"icon":"🔒"}'.encode("utf-8")

    def test_cjk(self):
        result = canonicalize({"text": "日本語"})
        assert result == '{"text":"日本語"}'.encode("utf-8")


class TestCanonicalEscaping:
    """Control characters and special characters are escaped."""

    def test_newline(self):
        result = canonicalize({"a": "line1\nline2"})
        assert result == b'{"a":"line1\\nline2"}'

    def test_tab(self):
        result = canonicalize({"a": "col1\tcol2"})
        assert result == b'{"a":"col1\\tcol2"}'

    def test_double_quote(self):
        result = canonicalize('hello"world')
        assert result == b'"hello\\"world"'

    def test_backslash(self):
        result = canonicalize("path\\to")
        assert result == b'"path\\\\to"'

    def test_control_characters(self):
        # U+0000 -> \u0000
        # U+001B (ESC) -> \u001b
        # U+0008 (Backspace) -> \b
        # U+000C (Form feed) -> \f
        # U+000D (CR) -> \r
        result = canonicalize({"a": "\x00\x1b\x08\x0c\r"})
        assert result == b'{"a":"\\u0000\\u001b\\b\\f\\r"}'


class TestCanonicalNumbers:
    """Integer range enforcement."""

    def test_safe_max(self):
        result = canonicalize(SAFE_INTEGER_MAX)
        assert result == b"9007199254740991"

    def test_safe_min(self):
        result = canonicalize(SAFE_INTEGER_MIN)
        assert result == b"-9007199254740991"

    def test_overflow_raises(self):
        with pytest.raises(ValueError, match="outside the safe"):
            canonicalize(SAFE_INTEGER_MAX + 1)

    def test_underflow_raises(self):
        with pytest.raises(ValueError, match="outside the safe"):
            canonicalize(SAFE_INTEGER_MIN - 1)

    def test_float_raises(self):
        with pytest.raises(ValueError, match="Floating-point"):
            canonicalize(3.14)

    def test_nan_raises(self):
        with pytest.raises(ValueError, match="Floating-point"):
            canonicalize(float("nan"))

    def test_infinity_raises(self):
        with pytest.raises(ValueError, match="Floating-point"):
            canonicalize(float("inf"))

    def test_negative_infinity_raises(self):
        with pytest.raises(ValueError, match="Floating-point"):
            canonicalize(float("-inf"))


class TestCanonicalWhitespace:
    """No whitespace between tokens."""

    def test_no_spaces(self):
        result = canonicalize({"a": 1, "b": [2, 3]})
        assert b" " not in result
        assert b"\n" not in result
        assert b"\t" not in result
