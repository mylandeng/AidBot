from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.auth import CurrentUser
from app.schemas.chat import RetrievalProvider
from app.services.rag_service import RAGService, RetrievedChunk
from app.services.tracing import end_trace, summarize_retrieved_chunks, summarize_user, text_fingerprint, trace_run


class RetrievalService:
    def __init__(self, local_rag_service: RAGService | None = None) -> None:
        self.local_rag_service = local_rag_service or RAGService()

    def retrieve(self, provider: RetrievalProvider, query: str, current_user: CurrentUser, db: Session) -> list[RetrievedChunk]:
        with trace_run(
            "AidBot Retrieve",
            "chain",
            inputs={"provider": provider, "query": text_fingerprint(query), "user": summarize_user(current_user)},
        ) as run:
            if provider == "local":
                chunks = self.local_rag_service.retrieve(query, current_user, db)
                end_trace(run, summarize_retrieved_chunks(chunks))
                return chunks
            end_trace(run, {"status": "error", "reason": "external_retrieval_not_configured"})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="外部知识库尚未配置，请先使用本地知识库。")

    def context_for_prompt(self, chunks: list[RetrievedChunk]) -> str:
        return self.local_rag_service.context_for_prompt(chunks)
