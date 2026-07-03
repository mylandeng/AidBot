from typing import Literal

from pydantic import BaseModel, Field


Confidence = Literal["low", "medium", "high"]
StrategyName = Literal["template", "rag", "local_kb", "langchain"]


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None
    product_line: str | None = None


class SourceCitation(BaseModel):
    title: str
    source_type: Literal["upload", "feishu", "manual", "ticket"]
    doc_id: str
    chunk_id: str
    score: float
    updated_at: str


class AnswerResult(BaseModel):
    strategy: StrategyName
    context: str
    sources: list[SourceCitation] = []
    confidence: Confidence = "low"
    handoff_required: bool = False
    handoff_reason: str = ""


class ChatResponse(BaseModel):
    answer: str
    solution_steps: list[str] = []
    confidence: Confidence = "low"
    sources: list[SourceCitation] = []
    handoff_required: bool = False
    handoff_reason: str = ""
