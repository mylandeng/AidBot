from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.schemas.access_key import AccessKeyCreateRequest, AccessKeyCreateResponse, AccessKeyListResponse, AccessKeyResponse, AccessKeyUpdateRequest
from app.schemas.auth import CurrentUser
from app.schemas.chat import ChatRequest
from app.services.access_key_service import AccessKeyService
from app.services.chat_service import ChatService

router = APIRouter(dependencies=[Depends(require_admin)])
access_key_service = AccessKeyService()
chat_service = ChatService()


@router.get("/status")
def admin_status() -> dict[str, str]:
    return {"status": "configured", "next": "access_key_management"}


@router.get("/access-keys", response_model=AccessKeyListResponse)
def list_access_keys(include_deleted: bool = Query(default=False), db: Session = Depends(get_db)) -> AccessKeyListResponse:
    return AccessKeyListResponse(items=[access_key_service.response(item) for item in access_key_service.list(db, include_deleted=include_deleted)])


@router.post("/access-keys", response_model=AccessKeyCreateResponse)
def create_access_key(request: AccessKeyCreateRequest, current_user: CurrentUser = Depends(require_admin), db: Session = Depends(get_db)) -> AccessKeyCreateResponse:
    item, plain_key = access_key_service.create(request, current_user, db)
    return AccessKeyCreateResponse(item=access_key_service.response(item), access_key=plain_key)


@router.patch("/access-keys/{key_id}", response_model=AccessKeyResponse)
def update_access_key(key_id: str, request: AccessKeyUpdateRequest, db: Session = Depends(get_db)) -> AccessKeyResponse:
    return access_key_service.response(access_key_service.update(key_id, request, db))


@router.post("/access-keys/{key_id}/disable", response_model=AccessKeyResponse)
def disable_access_key(key_id: str, db: Session = Depends(get_db)) -> AccessKeyResponse:
    return access_key_service.response(access_key_service.disable(key_id, db))


@router.post("/access-keys/{key_id}/enable", response_model=AccessKeyResponse)
def enable_access_key(key_id: str, db: Session = Depends(get_db)) -> AccessKeyResponse:
    return access_key_service.response(access_key_service.enable(key_id, db))


@router.delete("/access-keys/{key_id}", status_code=204)
def delete_access_key(key_id: str, db: Session = Depends(get_db)) -> None:
    access_key_service.delete(key_id, db)


@router.post("/chat/stream")
def stream_admin_chat(request: ChatRequest, current_user: CurrentUser = Depends(require_admin), db: Session = Depends(get_db)) -> StreamingResponse:
    return StreamingResponse(
        chat_service.stream_answer(request, current_user, db, include_debug=True),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
