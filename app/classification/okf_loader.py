from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from app.classification.models import CategoryDocument


KNOWLEDGE_ROOT = Path(__file__).resolve().parents[1] / "knowledge" / "commercial_banking"
CATEGORY_DIR = KNOWLEDGE_ROOT / "categories"
CATALOG_PATH = KNOWLEDGE_ROOT / "issue_catalog.md"


def _coerce_value(value: str) -> str | float:
    stripped = value.strip().strip('"').strip("'")
    try:
        return float(stripped)
    except ValueError:
        return stripped


def _parse_front_matter(markdown: str) -> dict[str, Any]:
    lines = markdown.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    metadata: dict[str, Any] = {}
    current_list_key: str | None = None

    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            break
        if not stripped:
            continue
        if stripped.startswith("- ") and current_list_key:
            metadata.setdefault(current_list_key, []).append(_coerce_value(stripped[2:]))
            continue
        if ":" not in stripped:
            continue

        key, raw_value = stripped.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if raw_value:
            metadata[key] = _coerce_value(raw_value)
            current_list_key = None
        else:
            metadata[key] = []
            current_list_key = key

    return metadata


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
