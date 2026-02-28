import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from sqlmodel import Session, SQLModel, create_engine

from app.config import settings
from app.models.feedback import QueryBuilderLog
from app.models.schemas import (
    ErrorResponse,
    FeedbackRequest,
    FeedbackResponse,
    GenerateRequest,
    GenerateResponse,
)
from app.services.assembler import build_message, build_response
from app.services.catalog import list_categories
from app.services.planner import generate_plan

logging.basicConfig(level=settings.log_level.upper())
logger = logging.getLogger(__name__)

engine = create_engine(settings.database_url, echo=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(
    title="Query Builder",
    description="AI-powered natural language to structured query converter",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate", response_model=GenerateResponse, responses={500: {"model": ErrorResponse}})
def generate(request: GenerateRequest):
    """Take a natural language prompt and return a structured query."""
    try:
        plan = generate_plan(request.prompt, request.options or None)
        message = build_message(plan)
        return build_response(plan, message)
    except Exception as e:
        logger.exception("Failed to generate query")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback", response_model=FeedbackResponse)
def feedback(request: FeedbackRequest):
    """Log user feedback/corrections for training."""
    log = QueryBuilderLog(
        user_id=request.user_id,
        input_prompt=request.input_prompt,
        generated_message=request.generated_message,
        final_message=request.final_message,
        rating=request.rating,
        was_edited=request.generated_message != request.final_message,
    )
    with Session(engine) as session:
        session.add(log)
        session.commit()
        session.refresh(log)
    return FeedbackResponse(success=True, id=log.id)


@app.get("/services")
def services():
    """Return the available service catalog."""
    return {"services": list_categories()}
