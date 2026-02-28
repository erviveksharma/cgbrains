from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from app.models.schemas import GenerateResponse, ParamsResponse, StepResponse
from app.models.step_types import QueryPlan, StepPlan

_TEMPLATES_DIR = Path(__file__).parent.parent / "prompts" / "templates"
_jinja_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATES_DIR)),
    trim_blocks=True,
    lstrip_blocks=True,
)

# Scripter operations that have dedicated templates
TEMPLATED_OPERATIONS = {"normalize", "sentiment", "keywords", "mentions_target", "narratives"}


def _render_step_message(step: StepPlan, step_number: int) -> str:
    """Render a single step into its message line."""
    operation = step.params.get("operation", "")

    # For scripter steps with known templates, use Jinja2
    if step.type == "scripter" and operation in TEMPLATED_OPERATIONS:
        template_map = {
            "normalize": "normalize.j2",
            "sentiment": "sentiment.j2",
            "keywords": "keywords.j2",
            "mentions_target": "target_check.j2",
            "narratives": "narratives.j2",
        }
        template = _jinja_env.get_template(template_map[operation])
        description = template.render(step=step, step_number=step_number)
    else:
        description = step.description

    return f"{step_number}. [{step.type}] {description}"


def _format_related_steps(related: list[int]) -> str:
    """Format related steps reference string."""
    if not related:
        return ""
    if len(related) == 1:
        return f" Related step {related[0]}."
    return f" Related steps {', '.join(str(s) for s in related)}."


def build_message(plan: QueryPlan) -> str:
    """
    Stage 2: Convert a QueryPlan into the formatted message string.

    Deterministic assembly - no LLM calls.
    """
    lines = []
    for i, step in enumerate(plan.steps, 1):
        line = _render_step_message(step, i)

        # Ensure related steps reference is in the description if not already
        if step.related_steps:
            related_str = _format_related_steps(step.related_steps)
            if "Related step" not in line:
                line = line.rstrip(".") + "." + related_str

        lines.append(line)

    return "\n".join(lines)


def build_response(plan: QueryPlan, message: str) -> GenerateResponse:
    """Build the full API response from a plan and assembled message."""
    steps = []
    for i, step in enumerate(plan.steps, 1):
        steps.append(StepResponse(
            number=i,
            type=step.type,
            service_category=step.service_category,
            initiator=step.initiator,
            description=step.description,
        ))

    params = ParamsResponse(
        source=plan.metadata.source,
        target_name=plan.metadata.target_name,
        target_url=plan.metadata.target_url,
        narrative_topics=plan.metadata.narrative_topics,
    )

    return GenerateResponse(
        success=True,
        message=message,
        steps=steps,
        params=params,
        step_count=len(steps),
    )
