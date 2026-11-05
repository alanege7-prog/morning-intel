"""Runtime configuration: one place that decides where data and secrets come from.

Locally:   keys from .env,               files in ./data
On Lambda: keys from Secrets Manager,    files in /tmp/data (the only writable path),
           last week's brief in S3 (Lambda's disk is wiped between runs).
"""
import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

ON_LAMBDA = bool(os.getenv("AWS_LAMBDA_FUNCTION_NAME"))
DATA_DIR = Path(os.getenv("DATA_DIR") or ("/tmp/data" if ON_LAMBDA else Path(__file__).parent / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

SECRET_ID = os.getenv("SECRET_ID", "")          # e.g. morning-agent/prod
STATE_BUCKET = os.getenv("STATE_BUCKET", "")    # S3 bucket for last_brief.json
STATE_KEY = "state/last_brief.json"
REQUIRED_KEYS = ("ANTHROPIC_API_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_IDS")


def load_secrets() -> None:
    """Put API keys into the environment for the rest of the code.
    Secret values are never logged."""
    if SECRET_ID:
        import boto3  # preinstalled on Lambda
        resp = boto3.client("secretsmanager").get_secret_value(SecretId=SECRET_ID)
        values = json.loads(resp["SecretString"])
        for key in REQUIRED_KEYS:
            if key in values:
                os.environ[key] = str(values[key]).strip()
        logger.info("Loaded %d keys from Secrets Manager (%s)", len(values), SECRET_ID)
    else:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).parent / ".env")

    missing = [k for k in REQUIRED_KEYS if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Missing required keys: {', '.join(missing)}")


def read_state() -> dict:
    """Last week's brief: from S3 on AWS, from data/ locally."""
    try:
        if STATE_BUCKET:
            import boto3
            obj = boto3.client("s3").get_object(Bucket=STATE_BUCKET, Key=STATE_KEY)
            return json.loads(obj["Body"].read())
        return json.loads((DATA_DIR / "last_brief.json").read_text(encoding="utf-8"))
    except Exception as exc:  # first run, missing object, bad JSON: start fresh
        logger.info("No previous brief found (%s)", type(exc).__name__)
        return {}


def write_state(brief: dict) -> None:
    body = json.dumps(brief, indent=2)
    try:
        if STATE_BUCKET:
            import boto3
            boto3.client("s3").put_object(
                Bucket=STATE_BUCKET, Key=STATE_KEY, Body=body.encode("utf-8"),
                ContentType="application/json",
            )
        else:
            (DATA_DIR / "last_brief.json").write_text(body, encoding="utf-8")
    except Exception as exc:
        logger.warning("Could not save brief for next week's review: %s", exc)
