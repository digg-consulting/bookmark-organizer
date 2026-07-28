"""Tests for the URL normalizer module."""
from __future__ import annotations

from bookmark_organizer.normalizer import normalize_url


def test_normalize_url_lowercase_scheme_host():
    assert normalize_url("HTTPS://Example.COM/Path") == "https://example.com/Path"


def test_normalize_url_trailing_slash():
    assert normalize_url("https://example.com/path/") == "https://example.com/path"


def test_normalize_url_default_ports():
    assert normalize_url("https://example.com:443/path") == "https://example.com/path"
    assert normalize_url("http://example.com:80/path") == "http://example.com/path"


def test_normalize_url_non_default_port():
    assert normalize_url("http://example.com:8080/path") == "http://example.com:8080/path"


def test_normalize_url_query_sort():
    assert normalize_url("https://example.com/path?b=2&a=1") == "https://example.com/path?a=1&b=2"


def test_normalize_url_empty():
    assert normalize_url("") == ""


def test_normalize_url_fragment_stripped():
    assert normalize_url("https://example.com/path#section") == "https://example.com/path"
