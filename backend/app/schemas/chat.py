from typing import Literal

from pydantic import BaseModel, Field


Confidence = Literal["low", "medium", "high"]
RetrievalProvider = Literal["local", "external"]
StrategyName = Literal["template", "rag", "local_kb", "langchain"]


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None
    product_line: str | None = None
    retrieval_provider: RetrievalProvider = "local"


class SourceCitation(BaseModel):
    title: str
    source_type: Literal["upload", "feishu", "manual", "ticket"]
    doc_id: str
    chunk_id: str
    score: float
    updated_at: str
    section_path: str = ""
    excerpt: str = ""


class AnswerResult(BaseModel):
    strategy: StrategyName
    context: str
    sources: list[SourceCitation] = Field(default_factory=list)
    confidence: Confidence = "low"
    handoff_required: bool = False
    handoff_reason: str = ""


class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    answer: str
    solution_steps: list[str] = Field(default_factory=list)
    confidence: Confidence = "low"
    sources: list[SourceCitation] = Field(default_factory=list)
    handoff_required: bool = False
    handoff_reason: str = ""


class UserChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    answer: str
    handoff_required: bool = False
    handoff_reason: str = ""


class MessageResponse(BaseModel):
    id: str
    role: Literal["user", "assistant"]
    content: str
    solution_steps: list[str] = Field(default_factory=list)
    sources: list[SourceCitation] = Field(default_factory=list)
    confidence: Confidence = "low"
    created_at: str


class ConversationSummary(BaseModel):
    id: str
    title: str
    product_line: str | None = None
    retrieval_provider: RetrievalProvider = "local"
    status: Literal["active", "archived"] = "active"
    updated_at: str
    message_count: int


class ConversationDetail(ConversationSummary):
    messages: list[MessageResponse]
