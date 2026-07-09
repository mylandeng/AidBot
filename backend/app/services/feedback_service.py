from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.conversation import Conversation, Message, utcnow
from app.models.feedback import AnswerFeedback
from app.schemas.auth import CurrentUser
from app.schemas.feedback import FeedbackCreateRequest, FeedbackItem, FeedbackStatusRequest


class FeedbackService:
    def list(self, current_user: CurrentUser, db: Session, status_filter: str | None = None) -> list[FeedbackItem]:
        query = (
            select(AnswerFeedback)
            .options(joinedload(AnswerFeedback.message), joinedload(AnswerFeedback.conversation))
            .order_by(AnswerFeedback.updated_at.desc())
        )
        if status_filter:
            query = query.where(AnswerFeedback.status == status_filter)
        if "admin" not in current_user.roles:
            query = query.where(AnswerFeedback.user_id == current_user.id)
        items = db.scalars(query).all()
        return [self._response(item, db) for item in items]

    def create(self, request: FeedbackCreateRequest, current_user: CurrentUser, db: Session) -> FeedbackItem:
        message = db.scalar(
            select(Message)
            .join(Conversation)
            .where(Message.id == request.message_id, Message.role == "assistant", Conversation.user_id == current_user.id)
        )
        if message is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Answer message not found")

        existing = db.scalar(select(AnswerFeedback).where(AnswerFeedback.message_id == message.id, AnswerFeedback.user_id == current_user.id))
        if existing:
            existing.rating = request.rating
            existing.tags = self._clean_tags(request.tags)
            existing.note = request.note.strip()
            existing.status = "pending"
            existing.updated_at = utcnow()
            item = existing
        else:
            item = AnswerFeedback(
                message_id=message.id,
                conversation_id=message.conversation_id,
                user_id=current_user.id,
                rating=request.rating,
                tags=self._clean_tags(request.tags),
                note=request.note.strip(),
            )
            db.add(item)

        db.commit()
        db.refresh(item)
        return self._response(item, db)

    def update_status(self, feedback_id: str, request: FeedbackStatusRequest, current_user: CurrentUser, db: Session) -> FeedbackItem:
        if "admin" not in current_user.roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
        item = db.scalar(select(AnswerFeedback).where(AnswerFeedback.id == feedback_id))
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
        item.status = request.status
        item.admin_note = request.admin_note.strip()
        item.updated_at = utcnow()
        db.commit()
        db.refresh(item)
        return self._response(item, db)

    def _response(self, item: AnswerFeedback, db: Session) -> FeedbackItem:
        answer = item.message or db.get(Message, item.message_id)
        question = self._question_before_answer(item.conversation_id, answer, db)
        return FeedbackItem(
            id=item.id,
            message_id=item.message_id,
            conversation_id=item.conversation_id,
            rating=item.rating,
            status=item.status,
            tags=item.tags,
            note=item.note,
            admin_note=item.admin_note,
            answer_preview=self._preview(answer.content if answer else ""),
            question_preview=self._preview(question.content if question else ""),
            source_count=len(answer.sources) if answer else 0,
            created_at=item.created_at.isoformat(),
            updated_at=item.updated_at.isoformat(),
        )

    def _question_before_answer(self, conversation_id: str, answer: Message | None, db: Session) -> Message | None:
        if answer is None:
            return None
        return db.scalar(
            select(Message)
            .where(Message.conversation_id == conversation_id, Message.role == "user", Message.created_at <= answer.created_at)
            .order_by(Message.created_at.desc())
        )

    def _clean_tags(self, tags: list[str]) -> list[str]:
        cleaned: list[str] = []
        for tag in tags:
            value = tag.strip()
            if value and value not in cleaned:
                cleaned.append(value[:40])
        return cleaned[:8]

    def _preview(self, content: str) -> str:
        compact = " ".join(content.split())
        return compact[:180]
