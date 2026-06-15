import json
import logging
import sys
from pathlib import Path

from fetcher.source_loader import load_sources
from fetcher.rss_fetcher import fetch_rss_sources
from fetcher.web_fetcher import fetch_web_sources
from analyzer.daily_analyzer import analyze_daily
from formatter.daily_formatter import format_daily
from delivery.telegram_delivery import deliver
from logger.run_logger import log_run

RAW_CONTENT_PATH = Path(__file__).parent / "data" / "raw_content.json"


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )


def main() -> None:
    setup_logging()
    log = logging.getLogger(__name__)
    log.info("=== Morning Intel — Daily Run Started ===")

    all_items: list[dict] = []
    brief: dict | None = None
    delivery_results: dict[str, bool] = {}

    try:
        # --- Fetch ---
        sources = load_sources()
        daily_sources = [s for s in sources if s["frequency"] == "daily"]
        log.info("Daily sources: %d", len(daily_sources))

        rss_items = fetch_rss_sources(daily_sources, window_hours=25)
        web_items = fetch_web_sources(daily_sources)
        all_items = rss_items + web_items
        log.info("Items fetched: %d (RSS: %d | Web: %d)", len(all_items), len(rss_items), len(web_items))

        RAW_CONTENT_PATH.write_text(
            json.dumps(all_items, indent=2, default=str), encoding="utf-8"
        )

        if not all_items:
            log.warning("No items fetched — brief will be thin or empty")

        # --- Analyze ---
        brief = analyze_daily(all_items)
        if brief is None:
            log.error("Analyzer failed — skipping delivery")
        else:
            # --- Format ---
            messages = format_daily(brief)
            if not messages:
                log.error("Formatter returned empty — skipping delivery")
            else:
                # --- Deliver ---
                delivery_results = deliver(messages)

    except Exception as exc:
        log.error("Unhandled error in daily pipeline: %s", exc, exc_info=True)

    finally:
        log_run("daily", all_items, brief, delivery_results)
        log.info("=== Morning Intel — Daily Run Complete ===")


if __name__ == "__main__":
    main()
