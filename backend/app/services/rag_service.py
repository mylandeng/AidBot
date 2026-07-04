from dataclasses import dataclass

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.models.knowledge import KnowledgeChunk, KnowledgeDocument, KnowledgeSource
from app.schemas.auth import CurrentUser
from app.schemas.chat import SourceCitation
from app.schemas.knowledge import KnowledgeSearchResult, KnowledgeSourceResponse, ManualKnowledgeCreate, MarkdownKnowledgeImport
from app.services.embedding_service import EmbeddingService


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: KnowledgeChunk
    source: KnowledgeSource
    document: KnowledgeDocument
    score: float

    def citation(self) -> SourceCitation:
        return SourceCitation(
            title=self.chunk.title,
            source_type=self.source.source_type,
            doc_id=self.document.id,
            chunk_id=self.chunk.id,
            score=round(self.score, 4),
            updated_at=self.chunk.updated_at.isoformat(),
        )

    def context_block(self) -> str:
        return f"标题：{self.chunk.title}\n来源ID：{self.chunk.id}\n内容：{self.chunk.content}"


class RAGService:
    def __init__(self, embedding_service: EmbeddingService | None = None) -> None:
        self.embedding_service = embedding_service or EmbeddingService()

    def create_manual_entry(self, payload: ManualKnowledgeCreate, current_user: CurrentUser, db: Session) -> KnowledgeSourceResponse:
        return self._create_entry(
            title=payload.title.strip(),
            content=payload.content.strip(),
            source_type="manual",
            visibility=payload.visibility,
            current_user=current_user,
            db=db,
        )

    def import_markdown(self, payload: MarkdownKnowledgeImport, current_user: CurrentUser, db: Session) -> KnowledgeSourceResponse:
        title = payload.title.strip() or payload.filename.strip()
        return self._create_entry(
            title=title,
            content=payload.content.strip(),
            source_type="upload",
            visibility=payload.visibility,
            current_user=current_user,
            db=db,
        )

    def _create_entry(
        self,
        title: str,
        content: str,
        source_type: str,
        visibility: str,
        current_user: CurrentUser,
        db: Session,
    ) -> KnowledgeSourceResponse:
        source = KnowledgeSource(
            title=title,
            source_type=source_type,
            visibility=visibility,
            owner_user_id=current_user.id,
        )
        document = KnowledgeDocument(title=title, content=content, source=source)
        for index, chunk_text in enumerate(self._split_text(content)):
            document.chunks.append(
                KnowledgeChunk(
                    source=source,
                    title=title,
                    content=chunk_text,
                    chunk_index=index,
                    embedding=self.embedding_service.embed(f"{title}\n{chunk_text}"),
                )
            )
        db.add(source)
        db.commit()
        db.refresh(source)
        return self._source_response(source)

    def list_sources(self, current_user: CurrentUser, db: Session) -> list[KnowledgeSourceResponse]:
        query = self._visible_sources_query(current_user).order_by(KnowledgeSource.updated_at.desc())
        return [self._source_response(source) for source in db.scalars(query).all()]

    def search(self, query_text: str, current_user: CurrentUser, db: Session, limit: int = 5) -> list[KnowledgeSearchResult]:
        return [
            KnowledgeSearchResult(
                **item.citation().model_dump(),
                preview=item.chunk.content[:180],
            )
            for item in self.retrieve(query_text, current_user, db, limit=limit)
        ]

    def retrieve(self, query_text: str, current_user: CurrentUser, db: Session, limit: int = 3) -> list[RetrievedChunk]:
        query_vector = self.embedding_service.embed(query_text)
        rows = db.execute(
            select(KnowledgeChunk, KnowledgeSource, KnowledgeDocument)
            .join(KnowledgeSource, KnowledgeChunk.source_id == KnowledgeSource.id)
            .join(KnowledgeDocument, KnowledgeChunk.document_id == KnowledgeDocument.id)
            .where(KnowledgeSource.status == "active")
            .where(or_(KnowledgeSource.visibility == "internal", KnowledgeSource.owner_user_id == current_user.id))
        ).all()
        scored = [
            RetrievedChunk(chunk=chunk, source=source, document=document, score=self.embedding_service.similarity(query_vector, chunk.embedding or []))
            for chunk, source, document in rows
        ]
        return [item for item in sorted(scored, key=lambda item: item.score, reverse=True) if item.score > 0.08][:limit]

    def context_for_prompt(self, chunks: list[RetrievedChunk]) -> str:
        if not chunks:
            return ""
        return "\n\n".join(f"[{index}] {chunk.context_block()}" for index, chunk in enumerate(chunks, start=1))

    def _visible_sources_query(self, current_user: CurrentUser) -> Select[tuple[KnowledgeSource]]:
        return select(KnowledgeSource).where(or_(KnowledgeSource.visibility == "internal", KnowledgeSource.owner_user_id == current_user.id))

    def _source_response(self, source: KnowledgeSource) -> KnowledgeSourceResponse:
        chunk_count = sum(len(document.chunks) for document in source.documents)
        return KnowledgeSourceResponse(
            id=source.id,
            title=source.title,
            source_type=source.source_type,
            visibility=source.visibility,
            status=source.status,
            chunk_count=chunk_count,
            updated_at=source.updated_at.isoformat(),
        )

    def _split_text(self, text: str, chunk_size: int = 900, overlap: int = 120) -> list[str]:
        compact = "\n".join(line.strip() for line in text.splitlines() if line.strip())
        if len(compact) <= chunk_size:
            return [compact]
        chunks: list[str] = []
        start = 0
        while start < len(compact):
            chunks.append(compact[start : start + chunk_size])
            start += chunk_size - overlap
        return chunks
