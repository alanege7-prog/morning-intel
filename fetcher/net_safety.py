"""Outbound request safety for the fetcher (SSRF protection).

Every URL the fetcher downloads must pass check_url():
  1. https only
  2. host on the allowlist (the configured sources' hosts + reviewed extras),
     exact match or a subdomain of an allowed host
  3. every IP the host resolves to must be a public (global) address,
     so nothing can point us at localhost, private networks or link-local
     ranges such as 169.254.169.254

safe_get() follows redirects manually and re-checks each hop, and stops
reading after MAX_BYTES so a hostile server can't exhaust memory.

Known residual risk: DNS can change between our check and the actual
connection (DNS rebinding). Accepted for this project: the Lambda runs
outside a VPC and has no instance metadata service to reach.
"""
import ipaddress
import logging
import socket
from functools import lru_cache
from urllib.parse import urljoin, urlparse

import requests

logger = logging.getLogger(__name__)

TIMEOUT = 15
MAX_BYTES = 5_000_000        # 5 MB per response
MAX_REDIRECTS = 3

# Hosts that sources legitimately redirect or publish feeds to.
# Every entry here was checked by hand; add new ones deliberately.
EXTRA_ALLOWED_HOSTS = {
    "feeds.feedburner.com",   # The Hacker News feed
    "cloud.google.com",       # Google Cloud Blog
    "rss.beehiiv.com",        # tl;dr sec newsletter platform (reviewed Nov 7, 2026)
}


class BlockedURLError(ValueError):
    """Raised when a URL fails the safety checks."""


@lru_cache(maxsize=1)
def allowed_hosts() -> frozenset[str]:
    from fetcher.source_loader import load_sources
    hosts = {urlparse(s["url"]).hostname for s in load_sources()}
    return frozenset(h.lower() for h in hosts if h) | EXTRA_ALLOWED_HOSTS


def _host_allowed(host: str) -> bool:
    host = host.lower().rstrip(".")
    return any(host == a or host.endswith("." + a) for a in allowed_hosts())


def check_url(url: str) -> None:
    """Raise BlockedURLError unless the URL is safe to fetch."""
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise BlockedURLError(f"non-https URL blocked: {url[:120]}")
    host = parsed.hostname
    if not host or not _host_allowed(host):
        raise BlockedURLError(f"host not on allowlist: {host}")
    try:
        infos = socket.getaddrinfo(host, parsed.port or 443, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise BlockedURLError(f"DNS lookup failed for {host}: {exc}") from exc
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if not ip.is_global:
            raise BlockedURLError(f"{host} resolves to non-public address {ip}")


class SafeResponse:
    def __init__(self, url: str, status: int, content: bytes, encoding: str | None):
        self.url = url
        self.status_code = status
        self.content = content
        self.encoding = encoding

    @property
    def text(self) -> str:
        return self.content.decode(self.encoding or "utf-8", errors="replace")


def safe_get(url: str, headers: dict | None = None) -> SafeResponse:
    """GET with allowlist + IP checks on every redirect hop and a size cap."""
    for _ in range(MAX_REDIRECTS + 1):
        check_url(url)
        resp = requests.get(url, headers=headers, timeout=TIMEOUT,
                            allow_redirects=False, stream=True)
        try:
            if resp.is_redirect or resp.status_code in (301, 302, 303, 307, 308):
                location = resp.headers.get("Location", "")
                if not location:
                    raise BlockedURLError(f"redirect without Location from {url[:120]}")
                url = urljoin(url, location)
                continue
            resp.raise_for_status()
            chunks, size = [], 0
            for chunk in resp.iter_content(chunk_size=65536):
                size += len(chunk)
                if size > MAX_BYTES:
                    raise BlockedURLError(f"response over {MAX_BYTES} bytes from {url[:120]}")
                chunks.append(chunk)
            return SafeResponse(url, resp.status_code, b"".join(chunks), resp.encoding)
        finally:
            resp.close()
    raise BlockedURLError(f"too many redirects starting at {url[:120]}")
