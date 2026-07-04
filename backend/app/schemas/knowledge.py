from typing import Literal

from pydantic import BaseModel, Field

SourceType = Literal["manual", "upload", "feishu", "ticket"]


class ManualKnowledgeCreate(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    content: str = Field(min_length=10, max_length=12000)
    visibility: Literal["internal", "private"] = "internal"


class MarkdownKnowledgeImport(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    content: str = Field(min_length=10, max_length=120000)
    filename: str = Field(min_length=1, max_length=240)
    visibility: Literal["internal", "private"] = "internal"


class KnowledgeSourceResponse(BaseModel):
    id: str
    title: str
    source_type: SourceType
    visibility: Literal["internal", "private"]
    status: str
    chunk_count: int
    updated_at: str


class KnowledgeSourceList(BaseModel):
    items: list[KnowledgeSourceResponse] = Field(default_factory=list)


class KnowledgeSearchResult(BaseModel):
    title: str
    source_type: SourceType
    doc_id: str
    chunk_id: str
    score: float
    updated_at: str
    preview: str


class KnowledgeSearchResponse(BaseModel):
    items: list[KnowledgeSearchResult] = Field(default_factory=list)
