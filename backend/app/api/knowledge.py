from fastapi import APIRouter

router = APIRouter()


@router.get("/sources")
def list_knowledge_sources() -> dict[str, list[object]]:
    return {"items": []}
