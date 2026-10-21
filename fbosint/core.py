"""Safe URL validation and evidence helpers. No Facebook scraping or network access."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
import hashlib

ALLOWED_HOSTS = {"facebook.com", "www.facebook.com", "m.facebook.com", "web.facebook.com", "fb.com", "www.fb.com"}

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def validate_facebook_url(value: str) -> str:
    """Return a normalized public Facebook URL or raise ValueError."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("URL is required")
    raw = value.strip()
    if any(ord(ch) < 32 for ch in raw):
        raise ValueError("Control characters are not allowed")
    parsed = urlsplit(raw)
    if parsed.scheme.lower() != "https":
        raise ValueError("Only HTTPS URLs are accepted")
    if parsed.username or parsed.password:
        raise ValueError("URLs containing credentials are not accepted")
    host = (parsed.hostname or "").lower().rstrip(".")
    if host not in ALLOWED_HOSTS:
        raise ValueError("Host must be a recognized Facebook domain")
    if parsed.port not in (None, 443):
        raise ValueError("Non-standard ports are not accepted")
    # Fragments are removed; query parameters are retained because some public URLs use them.
    return urlunsplit(("https", host, parsed.path or "/", parsed.query, ""))

def sha256_file(path: str | Path) -> tuple[str, int]:
    """Hash a user-selected local evidence file without uploading or copying it."""
    p = Path(path).expanduser()
    if not p.is_file():
        raise FileNotFoundError(f"Evidence file not found: {p}")
    digest = hashlib.sha256()
    size = 0
    with p.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size
