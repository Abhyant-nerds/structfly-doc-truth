from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.classification.okf_loader import load_category_documents
from app.classification.validate_knowledge import validate_knowledge
import app.classification.validate_knowledge as validator


class KnowledgeValidationTests(unittest.TestCase):
    def test_current_commercial_banking_bundle_is_valid(self) -> None:
        issues = validate_knowledge()

        self.assertEqual([], [issue.format() for issue in issues])

    def test_loader_reads_all_category_documents(self) -> None:
        load_category_documents.cache_clear()
        documents = load_category_documents()

        self.assertEqual(20, len(documents))
        self.assertTrue(all(document.description for document in documents))

    def test_validator_rejects_malformed_category_frontmatter(self) -> None:
        original_root = validator.KNOWLEDGE_ROOT
        original_category_dir = validator.CATEGORY_DIR

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            category_dir = root / "categories"
            category_dir.mkdir()
            (root / "index.md").write_text('---\nokf_version: "0.1"\n---\n\n# Test\n', encoding="utf-8")
            (root / "log.md").write_text("# Log\n\n## 2026-06-30\n\n* **Update**: Test.\n", encoding="utf-8")
            (category_dir / "index.md").write_text("# Categories\n", encoding="utf-8")
            (category_dir / "cat_001_bad.md").write_text("---\nid: CAT-001\n---\n\n# Bad\n", encoding="utf-8")

            validator.KNOWLEDGE_ROOT = root
            validator.CATEGORY_DIR = category_dir
            try:
                issues = validate_knowledge()
            finally:
                validator.KNOWLEDGE_ROOT = original_root
                validator.CATEGORY_DIR = original_category_dir

        messages = [issue.message for issue in issues]
        self.assertIn("frontmatter must include non-empty type", messages)
        self.assertIn("missing required category field: description", messages)


if __name__ == "__main__":
    unittest.main()
