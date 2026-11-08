"""Fetch all sources without calling Claude (free). Shows which sources work
and anything the SSRF allowlist blocked. Run: python check_sources.py"""
import collections
import logging
import sys

from fetcher.rss_fetcher import fetch_rss_sources
from fetcher.source_loader import load_sources
from fetcher.web_fetcher import fetch_web_sources

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s", stream=sys.stdout)

sources = load_sources()
items = fetch_rss_sources(sources, window_hours=168) + fetch_web_sources(sources)
counts = collections.Counter(i["source_name"] for i in items)

print("\n=== Results ===")
for s in sources:
    n = counts.get(s["name"], 0)
    print(f"{'OK  ' if n else 'NONE'} {n:>3}  {s['name']}")
print(f"\n{len(counts)}/{len(sources)} sources returned items, {len(items)} items total")
