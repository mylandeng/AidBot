from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.auth import CurrentUser
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()
chat_service = ChatService()


@router.post("", response_model=ChatResponse)
def create_chat_response(request: ChatRequest, current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)) -> ChatResponse:
    return chat_service.answer(request, current_user, db)


@router.post("/stream")
def stream_chat_response(request: ChatRequest, current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)) -> StreamingResponse:
    return StreamingResponse(
        chat_service.stream_answer(request, current_user, db),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
