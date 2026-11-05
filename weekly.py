import json
import logging
import sys
from pathlib import Path

from fetcher.source_loader import load_sources
from fetcher.rss_fetcher import fetch_rss_sources
from fetcher.web_fetcher import fetch_web_sources
from analyzer.weekly_analyzer import analyze_weekly
from formatter.weekly_formatter import format_weekly
from delivery.telegram_delivery import deliver
from logger.run_logger import log_run
import config

RAW_CONTENT_PATH = config.DATA_DIR / "raw_weekly_content.json"


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )


def main() -> dict:
    setup_logging()
    log = logging.getLogger(__name__)
    log.info("=== Morning Intel — Weekly Run Started ===")

    all_items: list[dict] = []
    brief: dict | None = None
    delivery_results: dict[str, bool] = {}

    try:
        # --- Fetch all 28 sources with 168-hour window ---
        sources = load_sources()
        log.info("Weekly sources: %d", len(sources))

        rss_items = fetch_rss_sources(sources, window_hours=168)
        web_items = fetch_web_sources(sources)
        all_items = rss_items + web_items
        log.info("Items fetched: %d (RSS: %d | Web: %d)", len(all_items), len(rss_items), len(web_items))

        RAW_CONTENT_PATH.write_text(
            json.dumps(all_items, indent=2, default=str), encoding="utf-8"
        )

        if not all_items:
            log.warning("No items fetched — digest will be thin or empty")

        # --- Analyze ---
        brief = analyze_weekly(all_items)
        if brief is None:
            log.error("Analyzer failed — skipping delivery")
        else:
            # --- Format ---
            messages = format_weekly(brief)
            if not messages:
                log.error("Formatter returned empty — skipping delivery")
            else:
                # --- Deliver ---
                delivery_results = deliver(messages)

    except Exception as exc:
        log.error("Unhandled error in weekly pipeline: %s", exc, exc_info=True)

    finally:
        log_run("weekly", all_items, brief, delivery_results)
        log.info("=== Morning Intel — Weekly Run Complete ===")

    delivered = bool(delivery_results) and all(delivery_results.values())
    return {
        "status": "success" if delivered else "failed",
        "items": len(all_items),
        "tokens": (brief or {}).get("_tokens_used", 0),
    }


if __name__ == "__main__":
    config.load_secrets()
    main()
