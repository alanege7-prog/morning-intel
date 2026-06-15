import json
import logging
import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "weekly_prompt.txt"
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 2500


def analyze_weekly(items: list[dict]) -> dict | None:
    if not items:
        logger.warning("No content items to analyze — skipping Claude API call")
        return None

    if not os.getenv("ANTHROPIC_API_KEY"):
        logger.error("ANTHROPIC_API_KEY not set — cannot run analyzer")
        return None

    try:
        system_prompt = _load_system_prompt()
        content_text = _format_content(items)

        client = anthropic.Anthropic()
        message = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            messages=[
                {"role": "user", "content": f"## THIS WEEK'S CONTENT\n\n{content_text}"}
            ],
        )

        tokens_used = message.usage.input_tokens + message.usage.output_tokens
        logger.info("Claude API call complete — tokens used: %d", tokens_used)

        raw = message.content[0].text if message.content else ""
        brief = _extract_json(raw)
        brief["_tokens_used"] = tokens_used
        return brief

    except json.JSONDecodeError as exc:
        logger.error("Failed to parse Claude response as JSON: %s", exc)
        return None
    except anthropic.APIError as exc:
        logger.error("Claude API error: %s", exc)
        return None
    except Exception as exc:
        logger.error("Unexpected error in weekly_analyzer: %s", exc)
        return None


def _load_system_prompt() -> str:
    template = PROMPT_PATH.read_text(encoding="utf-8")
    if "## THIS WEEK'S CONTENT" not in template:
        raise ValueError("weekly_prompt.txt is missing '## THIS WEEK'S CONTENT' section")
    system_part, _ = template.split("## THIS WEEK'S CONTENT", 1)
    return system_part.strip()


def _format_content(items: list[dict]) -> str:
    lines = []
    for item in items:
        lines.append(f"SOURCE: {item.get('source_name', 'Unknown')}")
        lines.append(f"TITLE: {item.get('title', '')}")
        if item.get("summary"):
            lines.append(f"SUMMARY: {item['summary']}")
        if item.get("link"):
            lines.append(f"LINK: {item['link']}")
        if item.get("published"):
            lines.append(f"PUBLISHED: {item['published']}")
        lines.append("")
    return "\n".join(lines)


def _extract_json(text: str) -> dict:
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise json.JSONDecodeError("No JSON object found in Claude response", text, 0)
    return json.loads(text[start : end + 1])
