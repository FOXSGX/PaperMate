from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class Paper(BaseModel):
    title: str
    authors: list[str] = Field(default_factory=list)
    summary: str
    url: Optional[str] = None
    published: Optional[str] = None
    categories: list[str] = Field(default_factory=list)


class SearchRequest(BaseModel):
    keyword: str = Field(..., min_length=2, examples=["Vision Transformer medical image segmentation"])
    max_results: int = Field(default=5, ge=1, le=20)


class SearchResponse(BaseModel):
    keyword: str
    total: int
    papers: list[Paper]


class SurveyRequest(BaseModel):
    topic: str = Field(..., min_length=2)
    max_papers: int = Field(default=5, ge=1, le=10)
    outline_style: str = Field(default="standard", examples=["standard", "method", "timeline"])


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    content_type: str
    chunks: int
    message: str


class QARequest(BaseModel):
    document_id: str
    question: str = Field(..., min_length=2)
    top_k: int = Field(default=3, ge=1, le=8)


class Citation(BaseModel):
    chunk_id: str
    score: float
    text: str


class QAResponse(BaseModel):
    answer: str
    citations: list[Citation]


class RewriteRequest(BaseModel):
    text: str = Field(..., min_length=5)
    style: str = Field(default="academic", examples=["academic", "concise", "polished"])


class RewriteResponse(BaseModel):
    original: str
    rewritten: str
    style: str


class FormatRequest(BaseModel):
    document_id: str
    template: str = Field(default="gb7713", examples=["gb7713", "journal"])


class FormatResponse(BaseModel):
    document_id: str
    template: str
    output_url: str
    message: str
