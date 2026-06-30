from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from app.classification.models import CategoryDocument


KNOWLEDGE_ROOT = Path(__file__).resolve().parents[1] / "knowledge" / "commercial_banking"
CATEGORY_DIR = KNOWLEDGE_ROOT / "categories"
CATALOG_PATH = KNOWLEDGE_ROOT / "issue_catalog.md"


def _parse_front_matter(markdown: str) -> dict[str, Any]:
    lines = markdown.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    try:
        end = lines[1:].index("---") + 1
    except ValueError:
        return {}

    front_matter = "\n".join(lines[1:end])
    parsed = yaml.safe_load(front_matter) or {}
    if not isinstance(parsed, dict):
        return {}
    return parsed


@lru_cache(maxsize=1)
def load_issue_catalog() -> str:
    if not CATALOG_PATH.exists():
        return ""
    return CATALOG_PATH.read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def load_category_documents() -> tuple[CategoryDocument, ...]:
    documents: list[CategoryDocument] = []
    if not CATEGORY_DIR.exists():
        return tuple()

    for path in sorted(CATEGORY_DIR.glob("cat_*.md")):
        markdown = path.read_text(encoding="utf-8")
        metadata = _parse_front_matter(markdown)
        category_id = str(metadata.get("id", "")).strip()
        title = str(metadata.get("title", "")).strip()
        if not category_id or not title:
            continue

        documents.append(
            CategoryDocument(
                category_id=category_id,
                title=title,
                description=str(metadata.get("description", "")).strip(),
                business_domain=str(metadata.get("business_domain", "")).strip(),
                owner=str(metadata.get("owner", "")).strip(),
                version=str(metadata.get("version", "")).strip(),
                status=str(metadata.get("status", "active")).strip(),
                tags=[str(tag) for tag in metadata.get("tags", [])],
                related=[str(item) for item in metadata.get("related", [])],
                review_threshold=float(metadata.get("review_threshold", 0.75) or 0.75),
                source_file=str(path.relative_to(KNOWLEDGE_ROOT.parent.parent)),
                markdown=markdown,
            )
        )

    return tuple(documents)


@lru_cache(maxsize=1)
def load_category_index() -> dict[str, CategoryDocument]:
    return {doc.category_id: doc for doc in load_category_documents()}


def get_category(category_id: str) -> CategoryDocument | None:
    return load_category_index().get(category_id)


def load_category_knowledge(category_ids: list[str]) -> str:
    docs = []
    for category_id in category_ids:
        doc = get_category(category_id)
        if doc:
            docs.append(doc.markdown)
    return "\n\n---\n\n".join(docs)
