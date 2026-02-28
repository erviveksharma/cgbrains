from typing import Literal

from pydantic import BaseModel, Field


class StepPlan(BaseModel):
    type: Literal["service", "scripter", "ai", "ai-image"]
    service_category: str | None = None  # Only for type=service
    initiator: str | None = None  # url, keyword, username, hashtag, image, etc.
    description: str  # Natural language step description
    related_steps: list[int] = Field(default_factory=list)  # References to previous steps
    params: dict = Field(default_factory=dict)  # Dynamic params (url, keyword, count, etc.)


class QueryMetadata(BaseModel):
    source: str | None = None
    target_name: str | None = None
    target_url: str | None = None
    target_id: str | None = None
    keywords: str | None = None  # Comma-separated
    narrative_topics: str | None = None  # Comma-separated
    benchmark_set: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    post_count: int = 50


class QueryPlan(BaseModel):
    steps: list[StepPlan]
    metadata: QueryMetadata
