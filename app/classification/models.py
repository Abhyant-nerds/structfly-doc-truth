from __future__ import annotations

from pydantic import BaseModel, Field


class EmailClassificationRequest(BaseModel):
    subject: str = ""
    body: str = Field(min_length=1)
    customer_id: str | None = None


class CategoryCandidate(BaseModel):
    category_id: str
    category_name: str
    score: float
    source_file: str
    matched_terms: list[str] = Field(default_factory=list)


class EmailClassificationResponse(BaseModel):
    final_category_id: str
    final_category_name: str
    confidence: float
    needs_review: bool
    routing_summary: dict
    candidates: list[CategoryCandidate] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    reason: str
    validation: dict = Field(default_factory=dict)
    processing_errors: list[dict[str, str]] = Field(default_factory=list)


class CategoryDocument(BaseModel):
    category_id: str
    title: str
    description: str = ""
    business_domain: str
    owner: str = ""
    version: str = ""
    status: str = "active"
    tags: list[str] = Field(default_factory=list)
    related: list[str] = Field(default_factory=list)
    review_threshold: float = 0.75
    source_file: str
    markdown: str
