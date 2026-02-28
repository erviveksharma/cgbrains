"""
Fine-tuning script for the query builder model.

Approach 1: LoRA with unsloth (local, recommended)
Approach 2: OpenAI fine-tuning API

Requires 500+ quality training pairs in training/data/pairs.jsonl
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
PAIRS_FILE = DATA_DIR / "pairs.jsonl"
CORRECTIONS_FILE = DATA_DIR / "corrections.jsonl"


def load_training_data() -> list[dict]:
    """Load and merge all training data sources."""
    pairs = []

    for path in [PAIRS_FILE, CORRECTIONS_FILE]:
        if path.exists():
            with open(path) as f:
                for line in f:
                    if line.strip():
                        pairs.append(json.loads(line))

    print(f"Loaded {len(pairs)} total training pairs")
    return pairs


def prepare_openai_format(pairs: list[dict], output_path: str) -> None:
    """Convert pairs to OpenAI fine-tuning JSONL format."""
    with open(output_path, "w") as f:
        for pair in pairs:
            entry = {
                "messages": [
                    {"role": "system", "content": "You are a query builder for a social media analytics platform."},
                    {"role": "user", "content": pair["input"]},
                    {"role": "assistant", "content": pair["message"]},
                ]
            }
            f.write(json.dumps(entry) + "\n")
    print(f"Wrote OpenAI format to {output_path}")


def prepare_unsloth_format(pairs: list[dict], output_path: str) -> None:
    """Convert pairs to unsloth/alpaca training format."""
    dataset = []
    for pair in pairs:
        dataset.append({
            "instruction": "Convert this natural language request into a structured query for the social media analytics platform.",
            "input": pair["input"],
            "output": pair["message"],
        })

    with open(output_path, "w") as f:
        json.dump(dataset, f, indent=2)
    print(f"Wrote unsloth format to {output_path}")


if __name__ == "__main__":
    pairs = load_training_data()

    if len(pairs) < 50:
        print(f"WARNING: Only {len(pairs)} pairs. Recommend 500+ for fine-tuning.")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    prepare_openai_format(pairs, str(DATA_DIR / "openai_finetune.jsonl"))
    prepare_unsloth_format(pairs, str(DATA_DIR / "unsloth_finetune.json"))
