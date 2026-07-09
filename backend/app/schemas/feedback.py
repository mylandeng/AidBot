from typing import Literal

from pydantic import BaseModel, Field


FeedbackRating = Literal["useful", "not_useful", "needs_review", "needs_human"]
FeedbackStatus = Literal["pending", "processing", "resolved", "ignored"]


class FeedbackCreateRequest(BaseModel):
    message_id: str = Field(min_length=1, max_length=64)
    rating: FeedbackRating
    tags: list[str] = Field(default_factory=list)
    note: str = Field(default="", max_length=1000)


class FeedbackStatusRequest(BaseModel):
    status: FeedbackStatus
    admin_note: str = Field(default="", max_length=1000)
