import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

LOG_PATH = Path(__file__).parent.parent / "data" / "run_log.json"
RETENTION_DAYS = 30


def log_run(
    run_type: str,
    items: list[dict],
    brief: dict | None,
    delivery_results: dict[str, bool],
) -> None:
    """Appends a run entry to run_log.json and prunes entries older than 30 days."""
    entry = _build_entry(run_type, items, brief, delivery_results)
    _write_entry(entry)


def _build_entry(
    run_type: str,
    items: list[dict],
    brief: dict | None,
    delivery_results: dict[str, bool],
) -> dict:
    source_ids = {item["source_id"] for item in items} if items else set()
    tokens_used = brief.get("_tokens_used", 0) if brief else 0

    if brief is None:
        status = "failed"
    elif not delivery_results:
        status = "failed"
    elif all(delivery_results.values()):
        status = "success"
    elif any(delivery_results.values()):
        status = "partial"
    else:
        status = "failed"

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "run_type": run_type,
        "sources_fetched": len(source_ids),
        "items_fetched": len(items) if items else 0,
        "tokens_used": tokens_used,
        "delivery": delivery_results,
        "status": status,
    }


def _write_entry(entry: dict) -> None:
    try:
        logs = _load_logs()
        logs.append(entry)
        logs = _prune(logs)
        LOG_PATH.write_text(json.dumps(logs, indent=2), encoding="utf-8")
        logger.info(
            "Run logged — status=%s | sources=%d | items=%d | tokens=%d",
            entry["status"],
            entry["sources_fetched"],
            entry["items_fetched"],
            entry["tokens_used"],
        )
    except Exception as exc:
        logger.error("Failed to write run log: %s", exc)


def _load_logs() -> list[dict]:
    if not LOG_PATH.exists():
        return []
    try:
        text = LOG_PATH.read_text(encoding="utf-8").strip()
        if not text:
            return []
        data = json.loads(text)
        return data if isinstance(data, list) else []
    except Exception as exc:
        logger.warning("Could not read run log, starting fresh: %s", exc)
        return []


def _prune(logs: list[dict]) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
    kept = []
    for entry in logs:
        try:
            if datetime.fromisoformat(entry["timestamp"]) >= cutoff:
                kept.append(entry)
        except Exception:
            kept.append(entry)
    return kept
