"""AWS Lambda entry point. Triggered weekly by EventBridge Scheduler."""
import logging

import config
import weekly

logging.getLogger().setLevel(logging.INFO)


def lambda_handler(event, context):
    config.load_secrets()
    result = weekly.main()
    if result.get("status") != "success":
        # Raising marks the invocation as failed -> Lambda "Errors" metric -> CloudWatch alarm.
        raise RuntimeError(f"Weekly run failed: {result}")
    return result
