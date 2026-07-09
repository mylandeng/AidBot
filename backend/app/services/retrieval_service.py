from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.auth import CurrentUser
from app.schemas.chat import RetrievalProvider
from app.services.rag_service import RAGService, RetrievedChunk


class RetrievalService:
    def __init__(self, local_rag_service: RAGService | None = None) -> None:
        self.local_rag_service = local_rag_service or RAGService()

    def retrieve(self, provider: RetrievalProvider, query: str, current_user: CurrentUser, db: Session) -> list[RetrievedChunk]:
        if provider == "local":
            return self.local_rag_service.retrieve(query, current_user, db)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="外部知识库尚未配置，请先使用本地知识库。")

    def context_for_prompt(self, chunks: list[RetrievedChunk]) -> str:
        return self.local_rag_service.context_for_prompt(chunks)
