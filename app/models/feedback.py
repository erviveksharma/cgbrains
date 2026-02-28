from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(UTC)


class QueryBuilderLog(SQLModel, table=True):
    __tablename__ = "query_builder_logs"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int
    input_prompt: str
    generated_message: str
    final_message: str
    rating: int = Field(ge=1, le=5)
    was_edited: bool = False
    created_at: datetime = Field(default_factory=_utcnow)
