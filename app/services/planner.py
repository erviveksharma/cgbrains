import logging

import instructor
import litellm

from app.config import settings
from app.models.step_types import QueryPlan
from app.prompts.system_prompt import build_system_prompt

logger = logging.getLogger(__name__)


def _get_client() -> instructor.Instructor:
    """Create an instructor-patched litellm client."""
    return instructor.from_litellm(litellm.completion)


def generate_plan(prompt: str, options: dict | None = None) -> QueryPlan:
    """
    Stage 1: Use LLM to generate a structured QueryPlan from natural language.

    Args:
        prompt: Natural language user request
        options: Optional overrides (post_count, date_from, date_to, etc.)

    Returns:
        QueryPlan with validated steps and metadata
    """
    client = _get_client()
    system_prompt = build_system_prompt()

    # Build the user message with options context
    user_message = prompt
    if options:
        option_parts = []
        for key, value in options.items():
            option_parts.append(f"{key}: {value}")
        if option_parts:
            user_message += f"\n\nAdditional parameters: {', '.join(option_parts)}"

    logger.info(f"Generating plan for: {prompt}")

    kwargs = {
        "model": settings.litellm_model,
        "response_model": QueryPlan,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "max_retries": 2,
    }

    if settings.litellm_api_base:
        kwargs["api_base"] = settings.litellm_api_base

    kwargs.update(settings.litellm_extra_kwargs)

    plan = client.chat.completions.create(**kwargs)

    # Apply option overrides to metadata
    if options:
        if "post_count" in options:
            plan.metadata.post_count = options["post_count"]
        if "date_from" in options:
            plan.metadata.date_from = options["date_from"]
        if "date_to" in options:
            plan.metadata.date_to = options["date_to"]

    logger.info(f"Generated plan with {len(plan.steps)} steps")
    return plan
