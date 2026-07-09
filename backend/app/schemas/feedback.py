from typing import Literal

from pydantic import BaseModel, Field


FeedbackRating = Literal["useful", "not_useful", "needs_review", "needs_human"]
FeedbackStatus = Literal["pending", "processing", "resolved", "ignored"]


class FeedbackCreateRequest(BaseModel):
    message_id: str = Field(min_length=1, max_length=64)
    rating: FeedbackRating
    tags: list[str] = Field(default_factory=list, max_length=8)
    note: str = Field(default="", max_length=1200)


class FeedbackStatusRequest(BaseModel):
    status: FeedbackStatus
    admin_note: str = Field(default="", max_length=2000)


class FeedbackItem(BaseModel):
    id: str
    message_id: str
    conversation_id: str
    rating: FeedbackRating
    status: FeedbackStatus
    tags: list[str] = Field(default_factory=list)
    note: str = ""
    admin_note: str = ""
    answer_preview: str
    question_preview: str
    source_count: int
    created_at: str
    updated_at: str


class FeedbackList(BaseModel):
    items: list[FeedbackItem]
