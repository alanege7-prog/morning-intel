import json
import logging
import urllib.robotparser
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from fetcher.net_safety import safe_get

logger = logging.getLogger(__name__)

_HEADERS = {"User-Agent": "MorningIntelAgent/1.0 (Web Scraper; respectful bot)"}
_MAX_HEADLINES = 10

_robots_cache: dict[str, urllib.robotparser.RobotFileParser] = {}


def fetch_web_sources(sources: list[dict]) -> list[dict]:
    results = []
    for source in sources:
        if source["type"] == "api":
            try:
                items = _fetch_api_source(source)
                results.extend(items)
            except Exception as exc:
                logger.error("API fetch failed for %s: %s", source["name"], exc)
        elif source["type"] == "web":
            try:
                items = _fetch_page(source)
                results.extend(items)
            except Exception as exc:
                logger.error("Web fetch failed for %s: %s", source["name"], exc)
    return results


def _fetch_api_source(source: dict) -> list[dict]:
    data = json.loads(safe_get(source["url"], headers=_HEADERS).content)

    items = []
    for entry in data[:_MAX_HEADLINES]:
        paper = entry.get("paper", entry)
        title = paper.get("title", "")
        summary = paper.get("summary", "")
        paper_id = paper.get("id", "")
        published = paper.get("publishedAt") or paper.get("submittedOnDailyAt")
        link = f"https://huggingface.co/papers/{paper_id}" if paper_id else source["url"]

        if not title:
            continue
        items.append({
            "source_id": source["id"],
            "source_name": source["name"],
            "source_url": source["url"],
            "category": source["category"],
            "frequency": source["frequency"],
            "title": title,
            "link": link,
            "summary": summary[:500] if summary else "",
            "published": published,
        })

    logger.info("Fetched %d papers from %s", len(items), source["name"])
    return items


def _fetch_page(source: dict) -> list[dict]:
    url = source["url"]

    if not _is_allowed(url):
        logger.warning("Robots.txt disallows fetching %s — skipping", url)
        return []

    resp = safe_get(url, headers=_HEADERS)

    soup = BeautifulSoup(resp.text, "lxml")
    headlines = _extract_headlines(soup, url)

    items = []
    for title, link in headlines[:_MAX_HEADLINES]:
        items.append({
            "source_id": source["id"],
            "source_name": source["name"],
            "source_url": url,
            "category": source["category"],
            "frequency": source["frequency"],
            "title": title,
            "link": link,
            "summary": "",
            "published": None,
        })

    logger.info("Fetched %d headlines from %s", len(items), source["name"])
    return items


def _extract_headlines(soup: BeautifulSoup, base_url: str) -> list[tuple[str, str]]:
    from urllib.parse import urljoin

    headlines = []
    seen = set()

    # Priority: article tags, then h2/h3 with links, then prominent anchor text
    candidates = []

    for article in soup.find_all("article"):
        for tag in article.find_all(["h1", "h2", "h3"]):
            a = tag.find("a", href=True)
            if a:
                candidates.append((a.get_text(strip=True), a["href"]))

    if not candidates:
        for tag in soup.find_all(["h2", "h3"]):
            a = tag.find("a", href=True)
            if a:
                candidates.append((a.get_text(strip=True), a["href"]))

    if not candidates:
        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True)
            if len(text) > 30:
                candidates.append((text, a["href"]))

    for title, href in candidates:
        if not title or title in seen:
            continue
        full_url = urljoin(base_url, href) if not href.startswith("http") else href
        seen.add(title)
        headlines.append((title, full_url))

    return headlines


def _is_allowed(url: str) -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    if robots_url not in _robots_cache:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        try:
            resp = safe_get(robots_url, headers=_HEADERS)
            rp.parse(resp.text.splitlines())
        except Exception:
            rp.allow_all = True
        _robots_cache[robots_url] = rp

    return _robots_cache[robots_url].can_fetch(_HEADERS["User-Agent"], url)
