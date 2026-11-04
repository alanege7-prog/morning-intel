"""Quick check: is the Anthropic key valid and reachable? Sends a 1-line request."""
import anthropic
from dotenv import load_dotenv

load_dotenv(".env")
try:
    client = anthropic.Anthropic(timeout=30, max_retries=0)
    reply = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=10,
        messages=[{"role": "user", "content": "Reply with: OK"}],
    )
    print("SUCCESS:", reply.content[0].text)
except anthropic.AuthenticationError:
    print("FAILED: key is invalid or revoked -> create a new key in the Anthropic Console")
except anthropic.PermissionDeniedError as e:
    print("FAILED: key has no access (billing/credits?):", e)
except anthropic.APIConnectionError as e:
    print("FAILED: cannot reach Anthropic (network/firewall/VPN):", e)
except anthropic.APIStatusError as e:
    print("FAILED:", e.status_code, e.message)
