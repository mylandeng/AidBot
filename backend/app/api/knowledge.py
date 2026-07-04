from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.auth import CurrentUser
from app.schemas.knowledge import KnowledgeSearchResponse, KnowledgeSourceList, KnowledgeSourceResponse, ManualKnowledgeCreate, MarkdownKnowledgeImport
from app.services.rag_service import RAGService

router = APIRouter()
rag_service = RAGService()


@router.get("/sources", response_model=KnowledgeSourceList)
def list_knowledge_sources(current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)) -> KnowledgeSourceList:
    return KnowledgeSourceList(items=rag_service.list_sources(current_user, db))


@router.post("/manual", response_model=KnowledgeSourceResponse)
def create_manual_knowledge(
    payload: ManualKnowledgeCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeSourceResponse:
    return rag_service.create_manual_entry(payload, current_user, db)


@router.post("/markdown", response_model=KnowledgeSourceResponse)
def import_markdown_knowledge(
    payload: MarkdownKnowledgeImport,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeSourceResponse:
    return rag_service.import_markdown(payload, current_user, db)


@router.get("/search", response_model=KnowledgeSearchResponse)
def search_knowledge(
    q: str = Query(min_length=1, max_length=500),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeSearchResponse:
    return KnowledgeSearchResponse(items=rag_service.search(q, current_user, db))
