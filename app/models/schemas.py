from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str
    options: dict = Field(default_factory=dict)


class StepResponse(BaseModel):
    number: int
    type: str
    service_category: str | None = None
    initiator: str | None = None
    description: str


class ParamsResponse(BaseModel):
    source: str | None = None
    target_name: str | None = None
    target_url: str | None = None
    attributes: str | None = None
    narrative_topics: str | None = None


class GenerateResponse(BaseModel):
    success: bool
    message: str
    steps: list[StepResponse]
    params: ParamsResponse
    step_count: int


class FeedbackRequest(BaseModel):
    user_id: int
    input_prompt: str
    generated_message: str
    final_message: str
    rating: int = Field(ge=1, le=5)


class FeedbackResponse(BaseModel):
    success: bool
    id: int


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
