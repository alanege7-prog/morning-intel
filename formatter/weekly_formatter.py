import html
import logging
import math
import re
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


CONFIDENCE_TAGS = {
    "high": "🟢 High confidence",
    "medium": "🟡 Medium confidence",
    "unverified": "🟠 Unverified",
}
VERDICT_TAGS = {"held": "✅ held", "missed": "❌ missed", "too early": "⏳ too early"}
WORDS_PER_MINUTE = 220


def _build_message(brief: dict) -> str:
    signals = brief.get("signals", [])
    body = []

    if brief.get("tldr"):
        body.append(f"<b>TL;DR:</b> {_e(brief['tldr'])}")

    for n, item in enumerate(signals, 1):
        block = [f"\n<b>{n} · {_e(item.get('headline', ''))}</b>"]
        if item.get("what"):
            block.append(_e(item["what"]))
        if item.get("for_you"):
            block.append(f"<b>For you:</b> {_e(item['for_you'])}")
        if item.get("action"):
            block.append(f"<b>Do:</b> {_e(item['action'])}")
        block.append(_source_line(item, with_confidence=True))
        body.append("\n".join(block))

    career = brief.get("career_signal") or {}
    if career.get("headline"):
        block = [f"\n🎓 <b>Career · {_e(career['headline'])}</b>"]
        if career.get("what"):
            block.append(_e(career["what"]))
        if career.get("action"):
            block.append(f"<b>Do:</b> {_e(career['action'])}")
        block.append(_source_line(career))
        body.append("\n".join(block))

    challenge = brief.get("challenge") or {}
    if challenge.get("claim"):
        block = [f"\n🥊 <b>Challenge your thesis</b>", _e(challenge["claim"])]
        if challenge.get("source"):
            block.append(_source_line(challenge))
        body.append("\n".join(block))

    review = brief.get("last_call_review") or {}
    verdict = (review.get("verdict") or "none").lower()
    if verdict in VERDICT_TAGS:
        body.append(f"\n🔁 <b>Last week's call:</b> {VERDICT_TAGS[verdict]} · {_e(review.get('note', ''))}")

    if brief.get("prediction"):
        body.append(f"\n🔮 <b>This week's call:</b> {_e(brief['prediction'])}")
    if brief.get("question"):
        body.append(f"\n❓ <b>Think about:</b> {_e(brief['question'])}")

    text = "\n".join(body)
    plain_words = len(re.sub(r"<[^>]+>", " ", text).split())
    minutes = max(1, math.ceil(plain_words / WORDS_PER_MINUTE))
    header = f"📊 <b>INTEL · {_format_week()} · {len(signals)} signals · {minutes} min</b>"
    return header + "\n\n" + text


def _source_line(item: dict, with_confidence: bool = False) -> str:
    parts = []
    if with_confidence:
        tag = CONFIDENCE_TAGS.get((item.get("confidence") or "").lower(), "")
        if tag:
            note = item.get("confidence_note")
            parts.append(f"{tag} ({_e(note)})" if note else tag)
    source = _e(item.get("source", ""))
    link = (item.get("link") or "").strip()
    if link.startswith("https://") or link.startswith("http://"):
        source = f'<a href="{html.escape(link, quote=True)}">{source or "source"}</a>'
    if source:
        parts.append(source)
    return "<i>" + " · ".join(parts) + "</i>" if parts else ""


def _format_week(date_str: str = "") -> str:
    """The digest covers the 7 days up to today. Computed in code, not by the
    model, because Claude was returning today's date as the start of the week."""
    end = datetime.now()
    start = end - timedelta(days=6)
    start_str = start.strftime(f"%B {start.day}")
    end_str = end.strftime(f"%B {end.day}, %Y")
    return f"{start_str}–{end_str}"


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
