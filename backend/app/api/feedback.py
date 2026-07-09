from fastapi import APIRouter, Depends

from app.core.security import require_admin

router = APIRouter(dependencies=[Depends(require_admin)])


@router.get("")
def list_feedback() -> dict[str, list[object]]:
    return {"items": []}
