from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.schemas.auth import CurrentUser
from app.schemas.feedback import FeedbackCreateRequest, FeedbackItem, FeedbackList, FeedbackStatus, FeedbackStatusRequest
from app.services.feedback_service import FeedbackService

router = APIRouter(dependencies=[Depends(require_admin)])
feedback_service = FeedbackService()


@router.get("", response_model=FeedbackList)
def list_feedback(
    status: FeedbackStatus | None = Query(default=None),
    product_line: str | None = Query(default=None, min_length=1, max_length=120),
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> FeedbackList:
    return FeedbackList(
        items=feedback_service.list(current_user, db, status, product_line),
        product_lines=feedback_service.product_lines(current_user, db),
    )


@router.post("", response_model=FeedbackItem)
def create_feedback(request: FeedbackCreateRequest, current_user: CurrentUser = Depends(require_admin), db: Session = Depends(get_db)) -> FeedbackItem:
    return feedback_service.create(request, current_user, db)


@router.patch("/{feedback_id}", response_model=FeedbackItem)
def update_feedback_status(feedback_id: str, request: FeedbackStatusRequest, current_user: CurrentUser = Depends(require_admin), db: Session = Depends(get_db)) -> FeedbackItem:
    return feedback_service.update_status(feedback_id, request, current_user, db)
