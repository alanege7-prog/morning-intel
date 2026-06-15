import logging
import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_API_URL = "https://api.telegram.org/bot{token}/sendMessage"
_TIMEOUT = 15
_INTER_MESSAGE_DELAY = 0.5  # seconds between parts when a brief is split


def deliver(messages: list[str]) -> dict[str, bool]:
    """
    Sends all messages to every configured Telegram chat.
    Returns {chat_id: success} for each recipient.
    If one chat fails, delivery continues to the rest.
    """
    if not messages:
        logger.error("No messages to deliver — skipping Telegram delivery")
        return {}

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_ids_raw = os.getenv("TELEGRAM_CHAT_IDS", "")

    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set — cannot deliver")
        return {}

    chat_ids = [cid.strip() for cid in chat_ids_raw.split(",") if cid.strip()]
    if not chat_ids:
        logger.error("TELEGRAM_CHAT_IDS not set or empty — no recipients configured")
        return {}

    results = {}
    for chat_id in chat_ids:
        results[chat_id] = _send_to_chat(token, chat_id, messages)

    delivered = sum(1 for ok in results.values() if ok)
    logger.info("Delivery complete: %d/%d chats received the brief", delivered, len(results))
    return results


def _send_to_chat(token: str, chat_id: str, messages: list[str]) -> bool:
    url = _API_URL.format(token=token)
    all_ok = True

    for i, text in enumerate(messages):
        try:
            resp = requests.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
                timeout=_TIMEOUT,
            )
            resp.raise_for_status()
            data = resp.json()

            if not data.get("ok"):
                logger.error(
                    "Telegram rejected message %d/%d to chat %s: %s",
                    i + 1, len(messages), chat_id,
                    data.get("description", "unknown error"),
                )
                all_ok = False
            else:
                logger.info(
                    "Delivered message %d/%d to chat %s",
                    i + 1, len(messages), chat_id,
                )

        except requests.HTTPError as exc:
            logger.error("HTTP error delivering to chat %s: %s", chat_id, exc)
            all_ok = False
        except requests.RequestException as exc:
            logger.error("Network error delivering to chat %s: %s", chat_id, exc)
            all_ok = False

        if i < len(messages) - 1:
            time.sleep(_INTER_MESSAGE_DELAY)

    return all_ok
