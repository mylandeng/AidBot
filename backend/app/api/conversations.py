from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_conversations() -> dict[str, list[object]]:
    return {"items": []}
