import logging
import time
from datetime import datetime, timezone, timedelta

import feedparser
from bs4 import BeautifulSoup

from fetcher.net_safety import BlockedURLError, safe_get

logger = logging.getLogger(__name__)

_HEADERS = {"User-Agent": "MorningIntelAgent/1.0 (RSS Reader)"}


def fetch_rss_sources(sources: list[dict], window_hours: int = 25) -> list[dict]:
    rss_sources = [s for s in sources if s["type"] == "rss"]
    results = []
    for source in rss_sources:
        try:
            entries = _fetch_feed(source, window_hours)
            results.extend(entries)
        except Exception as exc:
            logger.error("RSS fetch failed for %s: %s", source["name"], exc)
    return results


def _fetch_feed(source: dict, window_hours: int = 25) -> list[dict]:
    url = source["url"]
    resp = safe_get(url, headers=_HEADERS)
    feed = feedparser.parse(resp.content)

    # If the URL is a web page rather than a feed, look for a feed link on it.
    # The discovered URL is untrusted page content, so it goes through safe_get too.
    if not feed.entries:
        discovered = _autodiscover_feed_url(resp.text, resp.url)
        if discovered:
            try:
                feed = feedparser.parse(safe_get(discovered, headers=_HEADERS).content)
                logger.info("Autodiscovered feed URL for %s: %s", source["name"], discovered)
            except BlockedURLError as exc:
                logger.warning("Blocked autodiscovered feed for %s: %s", source["name"], exc)

    if not feed.entries:
        raise ValueError(f"No entries found (bozo={feed.get('bozo')}, exc={feed.get('bozo_exception')})")

    cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)
    entries = []

    for entry in feed.entries:
        published = _parse_date(entry)

        if published is not None and published < cutoff:
            continue

        entries.append({
            "source_id": source["id"],
            "source_name": source["name"],
            "source_url": source["url"],
            "category": source["category"],
            "frequency": source["frequency"],
            "title": _get(entry, "title"),
            "link": _get(entry, "link"),
            "summary": _get(entry, "summary"),
            "published": published.isoformat() if published else None,
        })

    logger.info("Fetched %d entries from %s", len(entries), source["name"])
    return entries


def _autodiscover_feed_url(html: str, base_url: str) -> str | None:
    """Return the first RSS/Atom link on an already-downloaded page (no network call)."""
    from urllib.parse import urljoin
    try:
        soup = BeautifulSoup(html, "lxml")
        for link in soup.find_all("link", type=lambda t: t and ("rss" in t or "atom" in t)):
            href = link.get("href", "").strip()
            if href:
                return urljoin(base_url, href)
    except Exception as exc:
        logger.debug("Autodiscovery failed for %s: %s", base_url, exc)
    return None


def _parse_date(entry) -> datetime | None:
    for field in ("published_parsed", "updated_parsed"):
        t = getattr(entry, field, None)
        if t:
            try:
                return datetime.fromtimestamp(time.mktime(t), tz=timezone.utc)
            except Exception:
                pass
    return None


def _get(entry, field: str) -> str:
    value = getattr(entry, field, "") or ""
    return value.strip()
