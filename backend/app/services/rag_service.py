import re
from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy import Select, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.conversation import utcnow
from app.models.knowledge import KnowledgeChunk, KnowledgeDocument, KnowledgeSource, KnowledgeSpace
from app.schemas.auth import CurrentUser
from app.schemas.chat import SourceCitation
from app.schemas.knowledge import (
    KnowledgeDocumentImport,
    KnowledgeSearchResult,
    KnowledgeSourceResponse,
    KnowledgeSpaceCreate,
    KnowledgeSpaceResponse,
    ManualKnowledgeCreate,
    MarkdownKnowledgeImport,
)
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService


def _clean_markdown_for_prompt(text: str) -> str:
    cleaned_lines: list[str] = []
    in_code_block = False

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("```") or line.startswith("~~~"):
            in_code_block = not in_code_block
            continue
        if in_code_block or not line:
            continue
        if re.fullmatch(r"\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?", line):
            continue
        line = re.sub(r"^\s{0,3}#{1,6}\s+", "", line)
        line = re.sub(r"^\s{0,3}>\s?", "", line)
        line = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", line)
        line = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", line)
        line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
        line = re.sub(r"`([^`]+)`", r"\1", line)
        line = re.sub(r"(\*\*|__)(.*?)\1", r"\2", line)
        line = re.sub(r"(\*|_)(.*?)\1", r"\2", line)
        line = re.sub(r"\s*\|\s*", "，", line)
        line = re.sub(r"\s+", " ", line).strip(" -")
        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


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
        return f"标题：{self.chunk.title}\n来源ID：{self.chunk.id}\n内容：{_clean_markdown_for_prompt(self.chunk.content)}"


class RAGService:
    chunk_size = 1800
    chunk_overlap = 250

    def __init__(self, embedding_service: EmbeddingService | None = None, document_service: DocumentService | None = None) -> None:
        self.embedding_service = embedding_service or EmbeddingService()
        self.document_service = document_service or DocumentService()

    def create_space(self, payload: KnowledgeSpaceCreate, current_user: CurrentUser, db: Session) -> KnowledgeSpaceResponse:
        space = KnowledgeSpace(
            name=payload.name.strip(),
            description=payload.description.strip(),
            visibility=payload.visibility,
            owner_user_id=current_user.id,
        )
        db.add(space)
        db.commit()
        db.refresh(space)
        return self._space_response(space)

    def list_spaces(self, current_user: CurrentUser, db: Session) -> list[KnowledgeSpaceResponse]:
        rows = db.scalars(
            self._visible_spaces_query(current_user)
            .where(KnowledgeSpace.status == "active")
            .options(selectinload(KnowledgeSpace.sources).selectinload(KnowledgeSource.documents).selectinload(KnowledgeDocument.chunks))
            .order_by(KnowledgeSpace.updated_at.desc())
        ).all()
        return [self._space_response(space) for space in rows]

    def delete_space(self, space_id: str, current_user: CurrentUser, db: Session) -> None:
        space = self._get_editable_space(space_id, current_user, db)
        db.delete(space)
        db.commit()

    def create_manual_entry(self, payload: ManualKnowledgeCreate, current_user: CurrentUser, db: Session) -> KnowledgeSourceResponse:
        return self._create_entry(
            title=payload.title.strip(),
            content=payload.content.strip(),
            source_type="manual",
            content_format="text",
            filename="",
            visibility=payload.visibility,
            space_id=payload.space_id,
            current_user=current_user,
            db=db,
        )

    def import_markdown(self, payload: MarkdownKnowledgeImport, current_user: CurrentUser, db: Session) -> KnowledgeSourceResponse:
        return self.import_document(
            KnowledgeDocumentImport(
                title=payload.title,
                content=payload.content,
                filename=payload.filename,
                content_format="markdown",
                visibility=payload.visibility,
                space_id=payload.space_id,
            ),
            current_user,
            db,
        )

    def import_document(self, payload: KnowledgeDocumentImport, current_user: CurrentUser, db: Session) -> KnowledgeSourceResponse:
        parsed_content = self.document_service.parse_text(payload.content, payload.content_format)
        if len(parsed_content) < 10:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Parsed document content is too short")
        return self._create_entry(
            title=payload.title.strip() or payload.filename.strip(),
            content=parsed_content,
            source_type="upload",
            content_format=payload.content_format,
            filename=payload.filename.strip(),
            visibility=payload.visibility,
            space_id=payload.space_id,
            current_user=current_user,
            db=db,
        )

    def _create_entry(
        self,
        title: str,
        content: str,
        source_type: str,
        content_format: str,
        filename: str,
        visibility: str,
        space_id: str | None,
        current_user: CurrentUser,
        db: Session,
    ) -> KnowledgeSourceResponse:
        space = self._resolve_space(space_id, visibility, current_user, db)
        source = KnowledgeSource(
            space=space,
            title=title,
            source_type=source_type,
            content_format=content_format,
            filename=filename,
            visibility=visibility,
            owner_user_id=current_user.id,
        )
        document = KnowledgeDocument(title=title, content=content, source=source)
        self._append_chunks(document, source, title, content)
        db.add(source)
        db.commit()
        db.refresh(source)
        return self._source_response(source)

    def reindex_source(self, source_id: str, current_user: CurrentUser, db: Session) -> KnowledgeSourceResponse:
        source = db.scalar(
            select(KnowledgeSource).where(KnowledgeSource.id == source_id, KnowledgeSource.owner_user_id == current_user.id)
        )
        if source is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge source not found")

        for document in source.documents:
            for chunk in list(document.chunks):
                db.delete(chunk)
            db.flush()
            self._append_chunks(document, source, document.title, document.content)
            document.updated_at = utcnow()
        source.updated_at = utcnow()
        db.commit()
        db.refresh(source)
        return self._source_response(source)

    def delete_source(self, source_id: str, current_user: CurrentUser, db: Session) -> None:
        source = db.scalar(select(KnowledgeSource).where(KnowledgeSource.id == source_id, KnowledgeSource.owner_user_id == current_user.id))
        if source is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge source not found")
        db.delete(source)
        db.commit()

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
            .outerjoin(KnowledgeSpace, KnowledgeSource.space_id == KnowledgeSpace.id)
            .where(KnowledgeSource.status == "active")
            .where(or_(KnowledgeSource.space_id.is_(None), KnowledgeSpace.status == "active"))
            .where(or_(KnowledgeSource.visibility == "internal", KnowledgeSource.owner_user_id == current_user.id))
            .where(or_(KnowledgeSource.space_id.is_(None), KnowledgeSpace.visibility == "internal", KnowledgeSpace.owner_user_id == current_user.id))
        ).all()
        query_terms = self._lexical_terms(query_text)
        scored = []
        for chunk, source, document in rows:
            vector_score = self.embedding_service.similarity(query_vector, chunk.embedding or [])
            searchable_text = "\n".join(
                part
                for part in [
                    source.space.name if source.space else "",
                    source.title,
                    source.filename,
                    source.content_format,
                    document.title,
                    chunk.content,
                ]
                if part
            )
            lexical_score = self._lexical_score(query_terms, searchable_text)
            scored.append(RetrievedChunk(chunk=chunk, source=source, document=document, score=(vector_score * 0.65) + (lexical_score * 0.55)))
        return [item for item in sorted(scored, key=lambda item: item.score, reverse=True) if item.score > 0.08][:limit]

    def context_for_prompt(self, chunks: list[RetrievedChunk]) -> str:
        if not chunks:
            return ""
        return "\n\n".join(f"[{index}] {chunk.context_block()}" for index, chunk in enumerate(chunks, start=1))

    def _visible_sources_query(self, current_user: CurrentUser) -> Select[tuple[KnowledgeSource]]:
        return select(KnowledgeSource).where(or_(KnowledgeSource.visibility == "internal", KnowledgeSource.owner_user_id == current_user.id))

    def _visible_spaces_query(self, current_user: CurrentUser) -> Select[tuple[KnowledgeSpace]]:
        return select(KnowledgeSpace).where(or_(KnowledgeSpace.visibility == "internal", KnowledgeSpace.owner_user_id == current_user.id))

    def _resolve_space(self, space_id: str | None, visibility: str, current_user: CurrentUser, db: Session) -> KnowledgeSpace:
        if space_id:
            return self._get_editable_space(space_id, current_user, db)
        space = db.scalar(
            select(KnowledgeSpace).where(
                KnowledgeSpace.owner_user_id == current_user.id,
                KnowledgeSpace.name == "默认知识空间",
                KnowledgeSpace.status == "active",
            )
        )
        if space is not None:
            return space
        space = KnowledgeSpace(
            name="默认知识空间",
            description="未指定知识库时自动归档的默认空间。",
            visibility=visibility,
            owner_user_id=current_user.id,
        )
        db.add(space)
        db.flush()
        return space

    def _get_editable_space(self, space_id: str, current_user: CurrentUser, db: Session) -> KnowledgeSpace:
        space = db.scalar(select(KnowledgeSpace).where(KnowledgeSpace.id == space_id, KnowledgeSpace.owner_user_id == current_user.id))
        if space is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge space not found")
        return space

    def _space_response(self, space: KnowledgeSpace) -> KnowledgeSpaceResponse:
        sources = [source for source in space.sources if source.status == "active"]
        chunk_count = sum(len(document.chunks) for source in sources for document in source.documents)
        return KnowledgeSpaceResponse(
            id=space.id,
            name=space.name,
            description=space.description,
            visibility=space.visibility,
            status=space.status,
            source_count=len(sources),
            chunk_count=chunk_count,
            updated_at=space.updated_at.isoformat(),
        )

    def _source_response(self, source: KnowledgeSource) -> KnowledgeSourceResponse:
        chunk_count = sum(len(document.chunks) for document in source.documents)
        return KnowledgeSourceResponse(
            id=source.id,
            space_id=source.space_id,
            space_name=source.space.name if source.space else None,
            title=source.title,
            source_type=source.source_type,
            content_format=source.content_format,
            filename=source.filename,
            visibility=source.visibility,
            status=source.status,
            chunk_count=chunk_count,
            updated_at=source.updated_at.isoformat(),
        )

    def _append_chunks(self, document: KnowledgeDocument, source: KnowledgeSource, title: str, content: str) -> None:
        embedding_prefix = "\n".join(
            part
            for part in [
                source.space.name if source.space else "",
                title,
                source.filename,
                source.content_format,
            ]
            if part
        )
        for index, chunk_text in enumerate(self._split_text(content)):
            document.chunks.append(
                KnowledgeChunk(
                    source=source,
                    title=title,
                    content=chunk_text,
                    chunk_index=index,
                    embedding=self.embedding_service.embed(f"{embedding_prefix}\n{chunk_text}"),
                )
            )

    def _split_text(self, text: str, chunk_size: int | None = None, overlap: int | None = None) -> list[str]:
        size = chunk_size or self.chunk_size
        overlap_size = overlap or self.chunk_overlap
        sections = self._markdown_sections(text)
        if not sections:
            return []
        chunks: list[str] = []
        current: list[str] = []
        current_length = 0
        for section in sections:
            if len(section) > size:
                if current:
                    chunks.append("\n\n".join(current))
                    current = []
                    current_length = 0
                chunks.extend(self._split_long_text(section, size, overlap_size))
                continue
            next_length = current_length + len(section) + (2 if current else 0)
            if current and next_length > size:
                chunks.append("\n\n".join(current))
                current = [section]
                current_length = len(section)
            else:
                current.append(section)
                current_length = next_length
        if current:
            chunks.append("\n\n".join(current))
        return chunks

    def _markdown_sections(self, text: str) -> list[str]:
        heading_pattern = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
        sections: list[str] = []
        heading_stack: list[tuple[int, str]] = []
        body: list[str] = []

        def flush() -> None:
            compact_body = "\n".join(line.strip() for line in body if line.strip()).strip()
            if not compact_body:
                return
            heading_path = " > ".join(title for _, title in heading_stack)
            sections.append(f"标题路径：{heading_path}\n{compact_body}" if heading_path else compact_body)
            body.clear()

        for raw_line in text.splitlines():
            line = raw_line.strip()
            match = heading_pattern.match(line)
            if match:
                flush()
                level = len(match.group(1))
                title = match.group(2).strip()
                heading_stack = [(item_level, item_title) for item_level, item_title in heading_stack if item_level < level]
                heading_stack.append((level, title))
                continue
            body.append(line)

        flush()
        if sections:
            return sections
        compact = "\n".join(line.strip() for line in text.splitlines() if line.strip()).strip()
        return [compact] if compact else []

    def _split_long_text(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        compact = "\n".join(line.strip() for line in text.splitlines() if line.strip())
        if len(compact) <= chunk_size:
            return [compact]
        chunks: list[str] = []
        start = 0
        while start < len(compact):
            chunks.append(compact[start : start + chunk_size])
            start += chunk_size - overlap
        return chunks

    def _lexical_terms(self, text: str) -> set[str]:
        lowered = text.lower()
        terms = {token for token in re.findall(r"[a-z0-9_]{2,}", lowered)}
        cjk_runs = re.findall(r"[\u4e00-\u9fff]+", lowered)
        for run in cjk_runs:
            if len(run) == 1:
                terms.add(run)
                continue
            terms.update(run[index : index + 2] for index in range(len(run) - 1))
        return terms

    def _lexical_score(self, query_terms: set[str], candidate_text: str) -> float:
        if not query_terms:
            return 0.0
        candidate_terms = self._lexical_terms(candidate_text)
        if not candidate_terms:
            return 0.0
        return len(query_terms & candidate_terms) / len(query_terms)
