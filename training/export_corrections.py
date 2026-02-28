"""
Export user-corrected pairs from the feedback database for training.

Reads from query_builder_logs table where was_edited=True,
producing high-quality training pairs.

Output: training/data/corrections.jsonl
"""

import json
from pathlib import Path

from sqlmodel import Session, create_engine, select

import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.models.feedback import QueryBuilderLog

OUTPUT_DIR = Path(__file__).parent / "data"
OUTPUT_FILE = OUTPUT_DIR / "corrections.jsonl"


def export_corrections() -> list[dict]:
    """Export edited feedback entries as training pairs."""
    engine = create_engine(settings.database_url)
    pairs = []

    with Session(engine) as session:
        statement = select(QueryBuilderLog).where(QueryBuilderLog.was_edited == True)
        logs = session.exec(statement).all()

        for log in logs:
            pairs.append({
                "input": log.input_prompt,
                "message": log.final_message,  # Use the corrected version
                "original_message": log.generated_message,
                "rating": log.rating,
                "source": "user_correction",
            })

    return pairs


def save_corrections(pairs: list[dict]) -> None:
    """Save correction pairs to JSONL."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        for pair in pairs:
            f.write(json.dumps(pair) + "\n")
    print(f"Exported {len(pairs)} correction pairs to {OUTPUT_FILE}")


if __name__ == "__main__":
    pairs = export_corrections()
    save_corrections(pairs)
