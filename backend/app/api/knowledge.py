from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.schemas.auth import CurrentUser
from app.schemas.knowledge import (
    KnowledgeDocumentImport,
    KnowledgeSearchResponse,
    KnowledgeSourceList,
    KnowledgeSourceResponse,
    KnowledgeSpaceCreate,
    KnowledgeSpaceList,
    KnowledgeSpaceResponse,
    ManualKnowledgeCreate,
    MarkdownKnowledgeImport,
)
from app.services.rag_service import RAGService

router = APIRouter(dependencies=[Depends(require_admin)])
rag_service = RAGService()


@router.get("/sources", response_model=KnowledgeSourceList)
def list_knowledge_sources(current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)) -> KnowledgeSourceList:
    return KnowledgeSourceList(items=rag_service.list_sources(current_user, db))


@router.get("/spaces", response_model=KnowledgeSpaceList)
def list_knowledge_spaces(current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)) -> KnowledgeSpaceList:
    return KnowledgeSpaceList(items=rag_service.list_spaces(current_user, db))


@router.post("/spaces", response_model=KnowledgeSpaceResponse)
def create_knowledge_space(
    payload: KnowledgeSpaceCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeSpaceResponse:
    return rag_service.create_space(payload, current_user, db)


@router.delete("/spaces/{space_id}", status_code=204)
def delete_knowledge_space(
    space_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    rag_service.delete_space(space_id, current_user, db)


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


@router.post("/documents", response_model=KnowledgeSourceResponse)
def import_knowledge_document(
    payload: KnowledgeDocumentImport,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeSourceResponse:
    return rag_service.import_document(payload, current_user, db)


@router.post("/sources/{source_id}/reindex", response_model=KnowledgeSourceResponse)
def reindex_knowledge_source(
    source_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeSourceResponse:
    return rag_service.reindex_source(source_id, current_user, db)


@router.delete("/sources/{source_id}", status_code=204)
def delete_knowledge_source(
    source_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    rag_service.delete_source(source_id, current_user, db)


@router.get("/search", response_model=KnowledgeSearchResponse)
def search_knowledge(
    q: str = Query(min_length=1, max_length=500),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeSearchResponse:
    return KnowledgeSearchResponse(items=rag_service.search(q, current_user, db))
