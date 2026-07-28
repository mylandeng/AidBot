from typing import Literal

from pydantic import BaseModel, Field

SourceType = Literal["manual", "upload", "feishu", "ticket"]
ContentFormat = Literal["text", "markdown", "html", "pdf"]


class ManualKnowledgeCreate(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    content: str = Field(min_length=10, max_length=12000)
    visibility: Literal["internal", "private"] = "internal"
    space_id: str | None = None


class MarkdownKnowledgeImport(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    content: str = Field(min_length=10, max_length=120000)
    filename: str = Field(min_length=1, max_length=240)
    visibility: Literal["internal", "private"] = "internal"
    space_id: str | None = None


class KnowledgeDocumentImport(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    content: str = Field(min_length=1, max_length=300000)
    filename: str = Field(default="", max_length=240)
    content_format: ContentFormat = "markdown"
    visibility: Literal["internal", "private"] = "internal"
    space_id: str | None = None


class KnowledgeSpaceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    product_line: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=1000)
    visibility: Literal["internal", "private"] = "internal"


class KnowledgeSpaceUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    product_line: str = Field(min_length=1, max_length=120)


class KnowledgeSpaceResponse(BaseModel):
    id: str
    name: str
    product_line: str | None = None
    description: str
    visibility: Literal["internal", "private"]
    status: str
    source_count: int
    chunk_count: int
    updated_at: str


class KnowledgeSpaceList(BaseModel):
    items: list[KnowledgeSpaceResponse] = Field(default_factory=list)


class KnowledgeSourceResponse(BaseModel):
    id: str
    space_id: str | None = None
    space_name: str | None = None
    title: str
    source_type: SourceType
    content_format: ContentFormat = "markdown"
    filename: str = ""
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
