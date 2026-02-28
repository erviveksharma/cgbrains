"""
Generate synthetic training pairs from production data.

Input sources:
1. messages.json (production queries) → reverse-generate NL prompts
2. Service catalog → generate prompts per service category

Output: training/data/pairs.jsonl
"""

import json
import sys
from pathlib import Path

import litellm

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings

OUTPUT_DIR = Path(__file__).parent / "data"
OUTPUT_FILE = OUTPUT_DIR / "pairs.jsonl"

REVERSE_PROMPT = """Given this structured query message for a social media analytics platform,
write a natural language prompt that a user would type to generate this query.

Query message:
{message}

Write 3-5 different natural language prompts that would produce this query.
Return as a JSON array of strings."""


def generate_from_messages(messages_path: str) -> list[dict]:
    """Generate NL→structured pairs from production messages.json."""
    with open(messages_path) as f:
        messages = json.load(f)

    pairs = []
    for msg in messages:
        # Call LLM to reverse-generate natural language prompts
        kwargs = {
            "model": settings.litellm_model,
            "messages": [
                {"role": "user", "content": REVERSE_PROMPT.format(message=msg["message"])},
            ],
        }
        if settings.litellm_api_base:
            kwargs["api_base"] = settings.litellm_api_base

        response = litellm.completion(**kwargs)
        try:
            prompts = json.loads(response.choices[0].message.content)
            for prompt in prompts:
                pairs.append({
                    "input": prompt,
                    "message": msg["message"],
                    "source": "reverse_generated",
                })
        except (json.JSONDecodeError, KeyError):
            continue

    return pairs


def save_pairs(pairs: list[dict]) -> None:
    """Save pairs to JSONL file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "a") as f:
        for pair in pairs:
            f.write(json.dumps(pair) + "\n")
    print(f"Saved {len(pairs)} pairs to {OUTPUT_FILE}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_synthetic.py <messages.json>")
        sys.exit(1)

    pairs = generate_from_messages(sys.argv[1])
    save_pairs(pairs)
