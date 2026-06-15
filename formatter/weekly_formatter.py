import html
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

TELEGRAM_MAX_CHARS = 4096


def format_weekly(brief: dict) -> list[str]:
    """
    Takes parsed weekly brief dict, returns list of Telegram-ready HTML message strings.
    Usually one message; splits into multiple if the digest exceeds 4096 chars.
    Returns empty list if formatting fails — caller must not deliver an empty brief.
    """
    if not brief:
        logger.error("Cannot format empty brief")
        return []

    try:
        message = _build_message(brief)
        return _split_message(message)
    except Exception as exc:
        logger.error("Failed to format weekly brief: %s", exc)
        return []


def _build_message(brief: dict) -> str:
    parts = []

    # Header
    week_str = _format_week(brief.get("week_of", ""))
    parts.append(f"📊 <b>WEEKLY INTEL DIGEST — {week_str}</b>")

    # Top Signals
    signals = brief.get("top_signals", [])
    if signals:
        parts.append("\n🏆 <b>TOP 3 SIGNALS OF THE WEEK</b>")
        for item in signals:
            signal = _e(item.get("signal", ""))
            what_happened = _e(item.get("what_happened", ""))
            why = _e(item.get("why_it_matters", ""))
            sources = item.get("sources", [])
            block = f"\n<b>{signal}</b>"
            if what_happened:
                block += f"\n{what_happened}"
            if why:
                block += f"\n→ <i>{why}</i>"
            if sources:
                block += f"\nSources: {_e(', '.join(sources))}"
            parts.append(block)

    # Market Gaps
    gaps = brief.get("market_gaps", [])
    if gaps:
        parts.append("\n🗺️ <b>MARKET GAPS SPOTTED</b>")
        for item in gaps:
            gap = _e(item.get("gap", ""))
            evidence = _e(item.get("evidence", ""))
            angle = _e(item.get("founder_angle", ""))
            block = f"\n<b>{gap}</b>"
            if evidence:
                block += f"\nEvidence: {evidence}"
            if angle:
                block += f"\nYour angle: {angle}"
            parts.append(block)

    # Velocity Watch
    velocity = brief.get("velocity_watch", [])
    if velocity:
        parts.append("\n📈 <b>VELOCITY WATCH</b>")
        for item in velocity:
            topic = _e(item.get("topic", ""))
            trajectory = _e(item.get("trajectory", ""))
            implication = _e(item.get("implication", ""))
            block = f"\n<b>{topic}</b>"
            if trajectory:
                block += f"\n{trajectory}"
            if implication:
                block += f"\n→ <i>{implication}</i>"
            parts.append(block)

    # Founder Focus
    focus = brief.get("founder_focus", {})
    if focus:
        recommendation = _e(focus.get("recommendation", ""))
        reasoning = _e(focus.get("reasoning", ""))
        parts.append("\n🎯 <b>WEEKLY FOUNDER FOCUS</b>")
        block = f"\n<b>{recommendation}</b>"
        if reasoning:
            block += f"\n{reasoning}"
        parts.append(block)

    return "\n".join(parts)


def _format_week(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        end = dt + timedelta(days=6)
        start_str = dt.strftime(f"%B {dt.day}")
        end_str = end.strftime(f"%B {end.day}, %Y")
        return f"WEEK OF {start_str}–{end_str}"
    except Exception:
        return date_str if date_str else "THIS WEEK"


def _e(text: str) -> str:
    return html.escape(str(text))


def _split_message(message: str) -> list[str]:
    if len(message) <= TELEGRAM_MAX_CHARS:
        return [message]

    chunks = []
    current = ""
    for line in message.split("\n\n"):
        candidate = (current + "\n\n" + line).strip() if current else line
        if len(candidate) > TELEGRAM_MAX_CHARS:
            if current:
                chunks.append(current.strip())
            current = line
        else:
            current = candidate

    if current:
        chunks.append(current.strip())

    logger.info("Digest split into %d message(s) for Telegram", len(chunks))
    return chunks if chunks else [message[:TELEGRAM_MAX_CHARS]]
