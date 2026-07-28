from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_internal_user
from app.schemas.auth import CurrentUser
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()
chat_service = ChatService()


@router.post("", response_model=ChatResponse)
def create_chat_response(request: ChatRequest, current_user: CurrentUser = Depends(require_internal_user), db: Session = Depends(get_db)) -> ChatResponse:
    return chat_service.answer(request, current_user, db)


@router.post("/stream")
def stream_chat_response(request: ChatRequest, http_request: Request, current_user: CurrentUser = Depends(require_internal_user), db: Session = Depends(get_db)) -> StreamingResponse:
    return StreamingResponse(
        chat_service.stream_answer(request, current_user, db, request_id=http_request.state.request_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
