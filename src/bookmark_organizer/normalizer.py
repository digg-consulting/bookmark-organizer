"""URL normalization for bookmark deduplication."""
from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

__all__ = ["normalize_url"]


def normalize_url(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url.strip())
    scheme = parsed.scheme.lower() if parsed.scheme else ""
    host = parsed.hostname.lower() if parsed.hostname else ""
    path = parsed.path.rstrip("/") if parsed.path else ""
    params = parsed.params
    query = _normalize_query(parsed.query)
    fragment = ""
    if scheme in ("http", "https") and host:
        if (scheme == "http" and parsed.port == 80) or (scheme == "https" and parsed.port == 443):
            netloc = host
        else:
            netloc = host
            if parsed.port:
                netloc = f"{host}:{parsed.port}"
    else:
        netloc = parsed.netloc.lower()

    return urlunparse((scheme, netloc, path, params, query, fragment))


def _normalize_query(query: str) -> str:
    if not query:
        return ""
    pairs = parse_qsl(query, keep_blank_values=True)
    pairs.sort()
    return urlencode(pairs, doseq=True)
