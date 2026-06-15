import html
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

TELEGRAM_MAX_CHARS = 4096


def format_daily(brief: dict) -> list[str]:
    """
    Takes parsed brief dict, returns list of Telegram-ready HTML message strings.
    Usually one message; splits into multiple if the brief exceeds 4096 chars.
    Returns empty list if formatting fails — caller must not deliver an empty brief.
    """
    if not brief:
        logger.error("Cannot format empty brief")
        return []

    try:
        message = _build_message(brief)
        return _split_message(message)
    except Exception as exc:
        logger.error("Failed to format daily brief: %s", exc)
        return []


def _build_message(brief: dict) -> str:
    parts = []

    # Header
    date_str = _format_date(brief.get("date", ""))
    parts.append(f"🌅 <b>MORNING INTEL — {date_str}</b>")

    # What's Moving Fast
    moving = brief.get("whats_moving_fast", [])
    if moving:
        parts.append("\n🔥 <b>WHAT'S MOVING FAST</b>")
        for item in moving:
            title = _e(item.get("title", ""))
            summary = _e(item.get("summary", ""))
            why = _e(item.get("why_it_matters", ""))
            source = _e(item.get("source", ""))
            block = f"\n<b>{title}</b>"
            if summary:
                block += f"\n{summary}"
            if why:
                block += f"\n→ <i>{why}</i>"
            if source:
                block += f"\nSource: {source}"
            parts.append(block)

    # Opportunity Gaps
    gaps = brief.get("opportunity_gaps", [])
    if gaps:
        parts.append("\n💡 <b>OPPORTUNITY GAPS</b>")
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

    # Watch Out
    threats = brief.get("watch_out", [])
    if threats:
        parts.append("\n⚠️ <b>WATCH OUT</b>")
        for item in threats:
            threat = _e(item.get("threat", ""))
            context = _e(item.get("context", ""))
            relevance = _e(item.get("relevance_to_smb", ""))
            block = f"\n<b>{threat}</b>"
            if context:
                block += f"\n{context}"
            if relevance:
                block += f"\n→ SMB angle: {relevance}"
            parts.append(block)

    # New Tools & Skills
    tools = brief.get("new_tools_and_skills", [])
    if tools:
        parts.append("\n🛠️ <b>NEW TOOLS & SKILLS</b>")
        tool_lines = []
        for item in tools:
            name = _e(item.get("name", ""))
            tool_type = _e(item.get("type", ""))
            why = _e(item.get("why_useful", ""))
            url = item.get("url", "")
            line = f"• <b>{name}</b>"
            if tool_type:
                line += f" [{tool_type}]"
            if why:
                line += f" — {why}"
            if url:
                line += f"\n  {_e(url)}"
            tool_lines.append(line)
        parts.append("\n" + "\n".join(tool_lines))

    # Founder Action
    action = brief.get("founder_action", {})
    if action:
        action_text = _e(action.get("action", ""))
        reasoning = _e(action.get("reasoning", ""))
        parts.append("\n📌 <b>FOUNDER ACTION</b>")
        block = f"\n<b>{action_text}</b>"
        if reasoning:
            block += f"\n{reasoning}"
        parts.append(block)

    return "\n".join(parts)


def _format_date(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime(f"%B {dt.day}, %Y")
    except Exception:
        return date_str


def _e(text: str) -> str:
    return html.escape(str(text))


def _split_message(message: str) -> list[str]:
    if len(message) <= TELEGRAM_MAX_CHARS:
        return [message]

    # Split at section boundaries to keep sections intact
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

    logger.info("Brief split into %d message(s) for Telegram", len(chunks))
    return chunks if chunks else [message[:TELEGRAM_MAX_CHARS]]
