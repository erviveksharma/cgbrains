"""
Evaluation suite for the query builder.

Metrics:
- JSON parse rate: Does the output parse as valid JSON?
- Step count accuracy: Correct number of steps?
- Service category match: Correct service selected?
- Initiator match: Correct initiator type?
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.planner import generate_plan

DATA_DIR = Path(__file__).parent / "data"
TEST_FILE = DATA_DIR / "test_set.jsonl"


def load_test_set() -> list[dict]:
    """Load the held-out test set."""
    if not TEST_FILE.exists():
        print(f"No test set found at {TEST_FILE}")
        return []

    pairs = []
    with open(TEST_FILE) as f:
        for line in f:
            if line.strip():
                pairs.append(json.loads(line))
    return pairs


def evaluate(test_pairs: list[dict]) -> dict:
    """Run evaluation on test pairs."""
    results = {
        "total": len(test_pairs),
        "parse_success": 0,
        "step_count_match": 0,
        "service_category_match": 0,
        "initiator_match": 0,
        "errors": [],
    }

    for pair in test_pairs:
        try:
            plan = generate_plan(pair["input"])
            results["parse_success"] += 1

            # Check step count
            expected_steps = pair.get("expected_step_count", len(pair.get("steps", [])))
            if len(plan.steps) == expected_steps:
                results["step_count_match"] += 1

            # Check first step service category
            if plan.steps and "expected_category" in pair:
                if plan.steps[0].service_category == pair["expected_category"]:
                    results["service_category_match"] += 1

            # Check first step initiator
            if plan.steps and "expected_initiator" in pair:
                if plan.steps[0].initiator == pair["expected_initiator"]:
                    results["initiator_match"] += 1

        except Exception as e:
            results["errors"].append({"input": pair["input"], "error": str(e)})

    # Calculate rates
    total = results["total"] or 1
    results["parse_rate"] = results["parse_success"] / total
    results["step_accuracy"] = results["step_count_match"] / total
    results["category_accuracy"] = results["service_category_match"] / total
    results["initiator_accuracy"] = results["initiator_match"] / total

    return results


def print_results(results: dict) -> None:
    """Pretty-print evaluation results."""
    print(f"\n{'='*50}")
    print(f"EVALUATION RESULTS ({results['total']} test cases)")
    print(f"{'='*50}")
    print(f"Parse success rate:     {results['parse_rate']:.1%}")
    print(f"Step count accuracy:    {results['step_accuracy']:.1%}")
    print(f"Category accuracy:      {results['category_accuracy']:.1%}")
    print(f"Initiator accuracy:     {results['initiator_accuracy']:.1%}")

    if results["errors"]:
        print(f"\nErrors ({len(results['errors'])}):")
        for err in results["errors"][:5]:
            print(f"  - {err['input'][:50]}... → {err['error']}")


if __name__ == "__main__":
    test_pairs = load_test_set()
    if not test_pairs:
        print("No test data. Create training/data/test_set.jsonl first.")
        sys.exit(1)

    results = evaluate(test_pairs)
    print_results(results)
