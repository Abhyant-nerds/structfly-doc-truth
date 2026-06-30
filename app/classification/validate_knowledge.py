from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


KNOWLEDGE_ROOT = Path(__file__).resolve().parents[1] / "knowledge" / "commercial_banking"
CATEGORY_DIR = KNOWLEDGE_ROOT / "categories"
RESERVED_FILENAMES = {"index.md", "log.md"}
CATEGORY_ID_RE = re.compile(r"^CAT-\d{3}$")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
DATE_HEADING_RE = re.compile(r"^## \d{4}-\d{2}-\d{2}$", re.MULTILINE)
ALLOWED_STATUSES = {"draft", "active", "deprecated"}


@dataclass(frozen=True)
class ValidationIssue:
    path: Path
    message: str

    def format(self) -> str:
        return f"{self.path.relative_to(KNOWLEDGE_ROOT)}: {self.message}"


def _split_frontmatter(markdown: str) -> tuple[dict[str, Any], str] | None:
    lines = markdown.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    try:
        end = lines[1:].index("---") + 1
    except ValueError:
        return None

    frontmatter = "\n".join(lines[1:end])
    body = "\n".join(lines[end + 1 :])
    parsed = yaml.safe_load(frontmatter) or {}
    if not isinstance(parsed, dict):
        return None
    return parsed, body


def _concept_files() -> list[Path]:
    return sorted(path for path in KNOWLEDGE_ROOT.rglob("*.md") if path.name not in RESERVED_FILENAMES)


def _category_files() -> list[Path]:
    return sorted(CATEGORY_DIR.glob("cat_*.md"))


def _category_id_from_filename(path: Path) -> str:
    number = path.stem.split("_", 2)[1]
    return f"CAT-{number}"


def _local_link_target_exists(source: Path, target: str) -> bool:
    clean_target = target.split("#", 1)[0].strip()
    if not clean_target:
        return True
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", clean_target):
        return True

    if clean_target.startswith("/"):
        candidate = KNOWLEDGE_ROOT / clean_target.lstrip("/")
    else:
        candidate = source.parent / clean_target

    if clean_target.endswith("/"):
        return candidate.is_dir() and (candidate / "index.md").exists()
    return candidate.exists()


def _validate_markdown_links(path: Path, body: str, issues: list[ValidationIssue]) -> None:
    for target in MARKDOWN_LINK_RE.findall(body):
        if not _local_link_target_exists(path, target):
            issues.append(ValidationIssue(path, f"broken local markdown link: {target}"))


def _validate_concepts(issues: list[ValidationIssue]) -> None:
    for path in _concept_files():
        split = _split_frontmatter(path.read_text(encoding="utf-8"))
        if split is None:
            issues.append(ValidationIssue(path, "missing or invalid YAML frontmatter"))
            continue
        metadata, body = split
        if not str(metadata.get("type", "")).strip():
            issues.append(ValidationIssue(path, "frontmatter must include non-empty type"))

        _validate_markdown_links(path, body, issues)


def _validate_indexes_and_logs(issues: list[ValidationIssue]) -> None:
    root_index = KNOWLEDGE_ROOT / "index.md"
    if not root_index.exists():
        issues.append(ValidationIssue(root_index, "missing root index.md"))
    else:
        split = _split_frontmatter(root_index.read_text(encoding="utf-8"))
        if split is None:
            issues.append(ValidationIssue(root_index, "root index.md must include parseable okf_version frontmatter"))
        elif str(split[0].get("okf_version", "")).strip() != "0.1":
            issues.append(ValidationIssue(root_index, 'root index.md must declare okf_version: "0.1"'))
        else:
            _validate_markdown_links(root_index, split[1], issues)

    categories_index = CATEGORY_DIR / "index.md"
    if not categories_index.exists():
        issues.append(ValidationIssue(categories_index, "missing categories/index.md"))
    elif categories_index.read_text(encoding="utf-8").lstrip().startswith("---"):
        issues.append(ValidationIssue(categories_index, "non-root index.md must not include frontmatter"))
    else:
        _validate_markdown_links(categories_index, categories_index.read_text(encoding="utf-8"), issues)

    log_path = KNOWLEDGE_ROOT / "log.md"
    if not log_path.exists():
        issues.append(ValidationIssue(log_path, "missing log.md"))
    else:
        log_body = log_path.read_text(encoding="utf-8")
        if not DATE_HEADING_RE.search(log_body):
            issues.append(ValidationIssue(log_path, "log.md must include YYYY-MM-DD date headings"))
        _validate_markdown_links(log_path, log_body, issues)


def _validate_categories(issues: list[ValidationIssue]) -> None:
    category_ids: dict[str, Path] = {}
    category_metadata: dict[str, dict[str, Any]] = {}

    for path in _category_files():
        split = _split_frontmatter(path.read_text(encoding="utf-8"))
        if split is None:
            continue

        metadata, _ = split
        category_id = str(metadata.get("id", "")).strip()
        if not CATEGORY_ID_RE.fullmatch(category_id):
            issues.append(ValidationIssue(path, "category id must match CAT-000 format"))
            continue

        expected_id = _category_id_from_filename(path)
        if category_id != expected_id:
            issues.append(ValidationIssue(path, f"filename implies {expected_id}, but frontmatter id is {category_id}"))

        if category_id in category_ids:
            issues.append(ValidationIssue(path, f"duplicate category id also used by {category_ids[category_id].name}"))
        category_ids[category_id] = path
        category_metadata[category_id] = metadata

        for field in ["title", "type", "description", "business_domain", "owner", "version", "status"]:
            if not str(metadata.get(field, "")).strip():
                issues.append(ValidationIssue(path, f"missing required category field: {field}"))

        status = str(metadata.get("status", "")).strip().lower()
        if status and status not in ALLOWED_STATUSES:
            issues.append(ValidationIssue(path, f"status must be one of {sorted(ALLOWED_STATUSES)}"))

        tags = metadata.get("tags", [])
        if not isinstance(tags, list) or not all(str(tag).strip() for tag in tags):
            issues.append(ValidationIssue(path, "tags must be a non-empty YAML list"))

        related = metadata.get("related", [])
        if not isinstance(related, list):
            issues.append(ValidationIssue(path, "related must be a YAML list"))

        try:
            threshold = float(metadata.get("review_threshold"))
        except (TypeError, ValueError):
            issues.append(ValidationIssue(path, "review_threshold must be numeric"))
        else:
            if not 0 <= threshold <= 1:
                issues.append(ValidationIssue(path, "review_threshold must be between 0 and 1"))

    if len(category_ids) != 20:
        issues.append(ValidationIssue(CATEGORY_DIR, f"expected 20 category files, found {len(category_ids)}"))

    for category_id, metadata in category_metadata.items():
        path = category_ids[category_id]
        for related_id in metadata.get("related", []):
            related_id = str(related_id).strip()
            if related_id not in category_ids:
                issues.append(ValidationIssue(path, f"related category does not exist: {related_id}"))


def validate_knowledge() -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not KNOWLEDGE_ROOT.exists():
        return [ValidationIssue(KNOWLEDGE_ROOT, "knowledge root does not exist")]

    _validate_concepts(issues)
    _validate_indexes_and_logs(issues)
    _validate_categories(issues)
    return issues


def main() -> int:
    issues = validate_knowledge()
    if issues:
        print("Knowledge validation failed:")
        for issue in issues:
            print(f"- {issue.format()}")
        return 1

    print("Knowledge validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
