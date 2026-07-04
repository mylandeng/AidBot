from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.conversation import Conversation, Message
from app.schemas.auth import CurrentUser
from app.schemas.chat import ConversationDetail, ConversationSummary, MessageResponse

router = APIRouter()


@router.get("", response_model=list[ConversationSummary])
def list_conversations(current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)) -> list[ConversationSummary]:
    rows = db.execute(select(Conversation, func.count(Message.id)).outerjoin(Message).where(Conversation.user_id == current_user.id).group_by(Conversation.id).order_by(Conversation.updated_at.desc())).all()
    return [ConversationSummary(id=item.id, title=item.title, product_line=item.product_line, updated_at=item.updated_at.isoformat(), message_count=count) for item, count in rows]


@router.get("/{conversation_id}", response_model=ConversationDetail)
def get_conversation(conversation_id: str, current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)) -> ConversationDetail:
    item = db.scalar(select(Conversation).options(selectinload(Conversation.messages)).where(Conversation.id == conversation_id, Conversation.user_id == current_user.id))
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    messages = [MessageResponse(id=m.id, role=m.role, content=m.content, solution_steps=m.solution_steps, sources=m.sources, confidence=m.confidence, created_at=m.created_at.isoformat()) for m in item.messages]
    return ConversationDetail(id=item.id, title=item.title, product_line=item.product_line, updated_at=item.updated_at.isoformat(), message_count=len(messages), messages=messages)
