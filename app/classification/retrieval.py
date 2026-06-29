from __future__ import annotations

import re
from collections import Counter
from typing import Any

from app.classification.models import CategoryCandidate, CategoryDocument
from app.classification.okf_loader import load_category_documents


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "our",
    "please",
    "the",
    "to",
    "we",
    "with",
    "your",
}

CATEGORY_ID_RE = re.compile(r"CAT-\d{3}", re.IGNORECASE)
TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_/-]*")


def extract_category_ids(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        source = " ".join(str(item) for item in value)
    else:
        source = str(value)
    seen: set[str] = set()
    category_ids: list[str] = []
    for match in CATEGORY_ID_RE.findall(source):
        category_id = match.upper()
        if category_id not in seen:
            seen.add(category_id)
            category_ids.append(category_id)
    return category_ids


def _tokens(text: str) -> list[str]:
    return [
        token.lower()
        for token in TOKEN_RE.findall(text)
        if len(token) > 2 and token.lower() not in STOPWORDS
    ]


def _category_text(doc: CategoryDocument) -> str:
    return " ".join([doc.category_id, doc.title, doc.business_domain, " ".join(doc.tags), doc.markdown])


def build_query_terms(subject: str, body: str, routing_summary: dict[str, Any]) -> list[str]:
    parts = [
        subject,
        body,
        str(routing_summary.get("primary_intent", "")),
        str(routing_summary.get("requested_action", "")),
        str(routing_summary.get("business_domain", "")),
        " ".join(str(item) for item in routing_summary.get("evidence_phrases", []) or []),
    ]
    return _tokens(" ".join(parts))


def retrieve_category_candidates(
    *,
    subject: str,
    body: str,
    routing_summary: dict[str, Any],
    top_k: int = 5,
) -> list[CategoryCandidate]:
    query_terms = build_query_terms(subject, body, routing_summary)
    query_counts = Counter(query_terms)
    routed_ids = set(extract_category_ids(routing_summary.get("candidate_categories")))
    routed_domain = str(routing_summary.get("business_domain", "")).lower()

    candidates: list[CategoryCandidate] = []
    for doc in load_category_documents():
        category_tokens = Counter(_tokens(_category_text(doc)))
        matched_terms = sorted(term for term in query_counts if category_tokens.get(term, 0) > 0)
        overlap_score = sum(min(query_counts[term], category_tokens[term]) for term in matched_terms)
        score = float(overlap_score)

        if doc.category_id in routed_ids:
            score += 8.0
        if routed_domain and routed_domain == doc.business_domain.lower():
            score += 3.0
        for tag in doc.tags:
            tag_tokens = set(_tokens(tag))
            if tag_tokens and tag_tokens.issubset(set(query_terms)):
                score += 2.0

        if doc.status.lower() != "active":
            score -= 5.0

        if score <= 0:
            continue

        candidates.append(
            CategoryCandidate(
                category_id=doc.category_id,
                category_name=doc.title,
                score=round(score, 3),
                source_file=doc.source_file,
                matched_terms=matched_terms[:12],
            )
        )

    candidates.sort(key=lambda item: (-item.score, item.category_id))
    return candidates[:top_k]
