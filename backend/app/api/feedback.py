from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_feedback() -> dict[str, list[object]]:
    return {"items": []}
