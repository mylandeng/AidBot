from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.conversation import Conversation, Message, utcnow
from app.schemas.auth import CurrentUser
from app.schemas.chat import ConversationDetail, ConversationSummary, MessageResponse

router = APIRouter()


@router.get("", response_model=list[ConversationSummary])
def list_conversations(
    q: str | None = Query(default=None, max_length=120),
    include_archived: bool = False,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ConversationSummary]:
    query = (
        select(Conversation, func.count(Message.id))
        .outerjoin(Message)
        .where(Conversation.user_id == current_user.id)
        .group_by(Conversation.id)
        .order_by(Conversation.updated_at.desc())
    )
    if not include_archived:
        query = query.where(Conversation.status == "active")
    if q and q.strip():
        keyword = f"%{q.strip()}%"
        query = query.where(or_(Conversation.title.ilike(keyword), Conversation.product_line.ilike(keyword), Message.content.ilike(keyword)))
    rows = db.execute(query).all()
    return [_summary_response(item, count) for item, count in rows]


@router.get("/{conversation_id}", response_model=ConversationDetail)
def get_conversation(conversation_id: str, current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)) -> ConversationDetail:
    item = db.scalar(select(Conversation).options(selectinload(Conversation.messages)).where(Conversation.id == conversation_id, Conversation.user_id == current_user.id))
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    include_debug = bool(set(current_user.roles).intersection({"admin", "support"}))
    messages = [
        MessageResponse(
            id=m.id,
            role=m.role,
            content=m.content,
            solution_steps=m.solution_steps if include_debug else [],
            sources=m.sources if include_debug else [],
            confidence=m.confidence if include_debug else "low",
            created_at=m.created_at.isoformat(),
        )
        for m in item.messages
    ]
    return ConversationDetail(
        id=item.id,
        title=item.title,
        product_line=item.product_line,
        retrieval_provider=item.retrieval_provider,
        status=item.status,
        updated_at=item.updated_at.isoformat(),
        message_count=len(messages),
        messages=messages,
    )


@router.post("/{conversation_id}/archive", response_model=ConversationSummary)
def archive_conversation(conversation_id: str, current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)) -> ConversationSummary:
    item = _get_owned_conversation(conversation_id, current_user, db)
    item.status = "archived"
    item.updated_at = utcnow()
    db.commit()
    db.refresh(item)
    return _summary_response(item, len(item.messages))


@router.post("/{conversation_id}/restore", response_model=ConversationSummary)
def restore_conversation(conversation_id: str, current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)) -> ConversationSummary:
    item = _get_owned_conversation(conversation_id, current_user, db)
    item.status = "active"
    item.updated_at = utcnow()
    db.commit()
    db.refresh(item)
    return _summary_response(item, len(item.messages))


@router.delete("/{conversation_id}", status_code=204)
def delete_conversation(conversation_id: str, current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)) -> None:
    item = _get_owned_conversation(conversation_id, current_user, db)
    db.delete(item)
    db.commit()


@router.delete("")
def delete_all_conversations(current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, int]:
    items = list(db.scalars(select(Conversation).where(Conversation.user_id == current_user.id)).all())
    deleted_count = len(items)
    for item in items:
        db.delete(item)
    db.commit()
    return {"deleted_count": deleted_count}


def _get_owned_conversation(conversation_id: str, current_user: CurrentUser, db: Session) -> Conversation:
    item = db.scalar(select(Conversation).options(selectinload(Conversation.messages)).where(Conversation.id == conversation_id, Conversation.user_id == current_user.id))
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return item


def _summary_response(item: Conversation, message_count: int) -> ConversationSummary:
    return ConversationSummary(
        id=item.id,
        title=item.title,
        product_line=item.product_line,
        retrieval_provider=item.retrieval_provider,
        status=item.status,
        updated_at=item.updated_at.isoformat(),
        message_count=message_count,
    )
