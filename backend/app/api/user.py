from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.auth import CurrentUser
from app.schemas.chat import ChatRequest
from app.schemas.feedback import FeedbackCreateRequest
from app.services.access_key_service import AccessKeyService
from app.services.chat_service import ChatService

router = APIRouter()
chat_service = ChatService()
access_key_service = AccessKeyService()


@router.post("/chat/stream")
def stream_user_chat(request: ChatRequest, current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)) -> StreamingResponse:
    access_key_service.ensure_session_key_is_usable(current_user.key_id, db)
    request = request.model_copy(update={"retrieval_provider": "local"})
    response = StreamingResponse(
        chat_service.stream_answer(request, current_user, db, include_debug=False),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
    access_key_service.record_request(current_user.key_id, db)
    return response


@router.post("/feedback")
def create_user_feedback(request: FeedbackCreateRequest, current_user: CurrentUser = Depends(get_current_user)) -> dict[str, str]:
    return {"id": request.message_id, "status": "received", "user_id": current_user.id}
