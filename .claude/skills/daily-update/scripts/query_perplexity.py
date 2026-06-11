#!/usr/bin/env python3
"""Send a research prompt to a Perplexity Sonar model via OpenRouter.

Usage:
    echo "<prompt text>" | python query_perplexity.py [model_id]

Reads the prompt from stdin (so multi-line prompts don't need shell quoting),
prints a JSON object with the model's `content` and any `citations` it returned.

Requires the OPENROUTER_API_KEY environment variable to be set.
"""
import json
import os
import sys
import urllib.error
import urllib.request

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "perplexity/sonar-pro"


def main():
    model = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODEL

    prompt = sys.stdin.read().strip()
    if not prompt:
        print("Usage: echo '<prompt text>' | python query_perplexity.py [model_id]", file=sys.stderr)
        sys.exit(1)

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print(
            "ERROR: OPENROUTER_API_KEY is not set.\n"
            "Set it with (PowerShell):\n"
            "  [System.Environment]::SetEnvironmentVariable('OPENROUTER_API_KEY', '<your-key>', 'User')\n"
            "then restart your terminal session so the variable is picked up.",
            file=sys.stderr,
        )
        sys.exit(1)

    # The user judges the report largely by checking sources, so we reinforce
    # citation discipline at the request level rather than relying on the model's
    # defaults — an uncited claim is one they can't verify and won't trust.
    system_prompt = (
        "You are a research assistant. Report only recent, verifiable developments. "
        "Cite a specific, real source URL for every factual claim. If you cannot find "
        "a credible source for something, say so explicitly rather than asserting it. "
        "Prefer primary sources and reputable wire services over aggregators or blogs."
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    }

    request = urllib.request.Request(
        OPENROUTER_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=240) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", errors="replace")
        print(f"ERROR: OpenRouter request failed ({err.code}): {detail}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as err:
        print(f"ERROR: Could not reach OpenRouter: {err.reason}", file=sys.stderr)
        sys.exit(1)

    choice = (body.get("choices") or [{}])[0]
    message = choice.get("message", {})
    content = message.get("content", "")
    citations = body.get("citations") or message.get("citations") or []

    print(json.dumps({"content": content, "citations": citations}, indent=2))


if __name__ == "__main__":
    main()
