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
from app.services.tracing import end_trace, summarize_retrieved_chunks, summarize_user, text_fingerprint, trace_run


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


def _heading_path_from_chunk(text: str) -> str:
    match = re.search(r"^标题路径：(.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def _parent_section_excerpt(document_text: str, heading_path: str, max_chars: int = 1200) -> str:
    if not heading_path:
        return ""

    sections = _markdown_sections_for_context(document_text)
    for path, body in sections:
        if path == heading_path:
            return body[:max_chars]
    return ""


def _markdown_sections_for_context(text: str) -> list[tuple[str, str]]:
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
    sections: list[tuple[str, str]] = []
    heading_stack: list[tuple[int, str]] = []
    body: list[str] = []

    def flush() -> None:
        compact_body = "\n".join(line.strip() for line in body if line.strip()).strip()
        if not compact_body:
            return
        heading_path = " > ".join(title for _, title in heading_stack)
        if heading_path:
            sections.append((heading_path, compact_body))
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
    return sections


def _unique_sorted(values: list[str] | set[str]) -> list[str]:
    return sorted({value.strip() for value in values if value and value.strip()})


def _merge_entity_metadata(*items: dict) -> dict:
    merged: dict[str, list[str]] = {}
    for item in items:
        for key, values in (item or {}).items():
            if isinstance(values, list):
                merged.setdefault(key, []).extend(str(value) for value in values)
    return {key: _unique_sorted(values) for key, values in merged.items()}


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
        heading_path = self.chunk.section_path or _heading_path_from_chunk(self.chunk.content)
        parent_excerpt = self.chunk.section_content or _parent_section_excerpt(self.document.content, heading_path)
        parts = [
            f"标题：{self.chunk.title}",
            f"来源ID：{self.chunk.id}",
        ]
        if heading_path:
            parts.append(f"父级章节：{heading_path}")
        if parent_excerpt:
            parts.append(f"章节回填：{_clean_markdown_for_prompt(parent_excerpt)}")
        parts.append(f"命中片段：{_clean_markdown_for_prompt(self.chunk.content)}")
        return "\n".join(parts)


class RAGService:
    chunk_size = 900
    chunk_overlap = 120
    candidate_pool_size = 20

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
        source_metadata = self._extract_entities("\n".join([title, filename, content_format, content]))
        source = KnowledgeSource(
            space=space,
            title=title,
            source_type=source_type,
            content_format=content_format,
            filename=filename,
            search_metadata=source_metadata,
            visibility=visibility,
            owner_user_id=current_user.id,
        )
        document = KnowledgeDocument(title=title, content=content, source=source, sections=self._section_metadata(content))
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
            document.sections = self._section_metadata(document.content)
            self._append_chunks(document, source, document.title, document.content)
            document.updated_at = utcnow()
        source.search_metadata = self._extract_entities("\n".join([source.title, source.filename, source.content_format, *[document.content for document in source.documents]]))
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
        with trace_run(
            "AidBot RAG Retrieve",
            "retriever",
            inputs={"query": text_fingerprint(query_text), "limit": limit, "user": summarize_user(current_user)},
        ) as run:
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
            exact_terms = self._exact_terms(query_text)
            query_entities = self._extract_entities(query_text)
            scored = []
            for chunk, source, document in rows:
                vector_score = (
                    self.embedding_service.similarity(query_vector, chunk.embedding or [])
                    if self.embedding_service.is_compatible(chunk.embedding_provider, chunk.embedding_model, chunk.embedding_dimensions)
                    else 0.0
                )
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
                exact_score = self._exact_score(exact_terms, searchable_text)
                title_score = self._exact_score(exact_terms, "\n".join(part for part in [source.title, document.title, chunk.title] if part))
                metadata_score = self._metadata_score(query_entities, _merge_entity_metadata(source.search_metadata or {}, chunk.entities or {}))
                hybrid_score = (vector_score * 0.4) + (lexical_score * 0.4) + (exact_score * 0.65) + (title_score * 0.25) + (metadata_score * 0.45)
                scored.append(RetrievedChunk(chunk=chunk, source=source, document=document, score=hybrid_score))
            ranked = [item for item in sorted(scored, key=lambda item: item.score, reverse=True) if item.score > 0.1]
            ranked = ranked[: max(self.candidate_pool_size, limit * 6)]
            chunks = self._diversify_sources(ranked, limit)
            end_trace(run, {"candidate_count": len(rows), "ranked_count": len(ranked), "chunks": summarize_retrieved_chunks(chunks)})
            return chunks

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
        chunk_index = 0
        for section in self._section_records(content):
            section_text = f"标题路径：{section['path']}\n{section['content']}" if section["path"] else section["content"]
            for chunk_text in self._split_long_text(section_text, self.chunk_size, self.chunk_overlap):
                entities = _merge_entity_metadata(
                    self._extract_entities("\n".join([source.title, source.filename, document.title, section["path"]])),
                    self._extract_entities(chunk_text),
                )
                document.chunks.append(
                    KnowledgeChunk(
                        source=source,
                        title=title,
                        content=chunk_text,
                        section_path=section["path"],
                        section_content=section["content"],
                        entities=entities,
                        chunk_index=chunk_index,
                        embedding=self.embedding_service.embed(f"{embedding_prefix}\n{section['path']}\n{chunk_text}"),
                        embedding_provider=self.embedding_service.provider_name,
                        embedding_model=self.embedding_service.model_name,
                        embedding_dimensions=self.embedding_service.dimensions,
                    )
                )
                chunk_index += 1

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

    def _section_records(self, text: str) -> list[dict[str, str]]:
        sections = _markdown_sections_for_context(text)
        if sections:
            return [{"path": path, "content": body} for path, body in sections]
        compact = "\n".join(line.strip() for line in text.splitlines() if line.strip()).strip()
        return [{"path": "", "content": compact}] if compact else []

    def _section_metadata(self, text: str) -> list[dict[str, object]]:
        return [
            {
                "path": section["path"],
                "length": len(section["content"]),
                "entities": self._extract_entities("\n".join([section["path"], section["content"]])),
            }
            for section in self._section_records(text)
        ]

    def _split_long_text(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        compact = "\n".join(line.strip() for line in text.splitlines() if line.strip())
        if len(compact) <= chunk_size:
            return [compact]
        heading_path = _heading_path_from_chunk(compact)
        if heading_path:
            compact = re.sub(r"^标题路径：.+\n?", "", compact, count=1)
        prefix = f"标题路径：{heading_path}\n" if heading_path else ""
        body_size = max(chunk_size - len(prefix), 200)
        step = max(body_size - overlap, 1)
        chunks: list[str] = []
        start = 0
        while start < len(compact):
            chunks.append(f"{prefix}{compact[start : start + body_size]}")
            start += step
        return chunks

    def _diversify_sources(self, ranked: list[RetrievedChunk], limit: int) -> list[RetrievedChunk]:
        if limit <= 0:
            return []

        selected: list[RetrievedChunk] = []
        seen_sources: set[str] = set()
        for item in ranked:
            if item.source.id in seen_sources:
                continue
            selected.append(item)
            seen_sources.add(item.source.id)
            if len(selected) >= limit:
                return selected

        for item in ranked:
            if item in selected:
                continue
            selected.append(item)
            if len(selected) >= limit:
                break
        return selected

    def _lexical_terms(self, text: str) -> set[str]:
        lowered = text.lower()
        terms = {token for token in re.findall(r"[a-z0-9_]{2,}", lowered)}
        cjk_runs = re.findall(r"[\u4e00-\u9fff]+", lowered)
        for run in cjk_runs:
            terms.update(run)
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

    def _exact_terms(self, text: str) -> set[str]:
        lowered = text.lower()
        terms = {token for token in re.findall(r"[a-z0-9]+(?:[-_][a-z0-9]+)+|[a-z0-9]{2,}", lowered)}
        terms.update(re.findall(r"\d+(?:\.\d+)+", lowered))
        terms.update(re.findall(r"[\u4e00-\u9fff]{2,}", lowered))
        return terms

    def _exact_score(self, query_terms: set[str], candidate_text: str) -> float:
        if not query_terms:
            return 0.0
        lowered = candidate_text.lower()
        return sum(1 for term in query_terms if term in lowered) / len(query_terms)

    def _extract_entities(self, text: str) -> dict[str, list[str]]:
        products = re.findall(r"\b[A-Z]{1,8}[A-Z0-9]*-\d+[A-Z0-9-]*\b", text, flags=re.IGNORECASE)
        fault_codes = re.findall(r"\b(?:E|ERR|ERROR|F|LED)\d{1,5}\b", text, flags=re.IGNORECASE)
        versions = re.findall(r"\b(?:v|版本)?\d+\.\d+(?:\.\d+)?\b", text, flags=re.IGNORECASE)
        component_terms = [
            "App",
            "DNS",
            "LED",
            "主控",
            "传感器",
            "充电器",
            "固件",
            "指示灯",
            "电池",
            "电源",
            "线束",
            "网关",
            "芯片",
            "路由器",
        ]
        components = [term for term in component_terms if re.search(re.escape(term), text, flags=re.IGNORECASE)]
        return {
            "products": _unique_sorted(value.upper() for value in products),
            "fault_codes": _unique_sorted(value.upper() for value in fault_codes),
            "versions": _unique_sorted(value.lower().lstrip("v").removeprefix("版本") for value in versions),
            "components": _unique_sorted(components),
        }

    def _metadata_score(self, query_entities: dict[str, list[str]], candidate_entities: dict[str, list[str]]) -> float:
        query_values = {value for values in query_entities.values() for value in values}
        if not query_values:
            return 0.0
        candidate_values = {value for values in candidate_entities.values() for value in values}
        if not candidate_values:
            return 0.0
        return len(query_values & candidate_values) / len(query_values)
