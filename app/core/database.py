from __future__ import annotations

import json
import re
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


class ReviewStore:
    def __init__(self, db_path: str, upload_storage_dir: str):
        self.db_path = Path(db_path)
        self.upload_storage_dir = Path(upload_storage_dir)

    def initialize(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.upload_storage_dir.mkdir(parents=True, exist_ok=True)
        with self.connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS use_cases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS review_batches (
                    id TEXT PRIMARY KEY,
                    use_case_id INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    reviewed_at TEXT,
                    reviewed_by TEXT,
                    FOREIGN KEY (use_case_id) REFERENCES use_cases(id)
                );

                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_id TEXT NOT NULL,
                    document_id TEXT NOT NULL UNIQUE,
                    filename TEXT NOT NULL,
                    stored_file_path TEXT,
                    mime_type TEXT,
                    source_type TEXT NOT NULL,
                    document_type_guess TEXT,
                    processing_errors_json TEXT NOT NULL,
                    draft_fields_json TEXT NOT NULL,
                    final_fields_json TEXT NOT NULL,
                    review_status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (batch_id) REFERENCES review_batches(id)
                );
                """
            )
            columns = {
                row["name"]
                for row in conn.execute("PRAGMA table_info(documents)").fetchall()
            }
            if "stored_file_path" not in columns:
                conn.execute("ALTER TABLE documents ADD COLUMN stored_file_path TEXT")

    def healthcheck(self) -> dict[str, Any]:
        expected_tables = {"use_cases", "review_batches", "documents"}
        with self.connection() as conn:
            rows = conn.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                """
            ).fetchall()

        existing_tables = {str(row["name"]) for row in rows}
        return {
            "db_path": str(self.db_path),
            "upload_storage_dir": str(self.upload_storage_dir),
            "db_exists": self.db_path.exists(),
            "expected_tables": sorted(expected_tables),
            "existing_tables": sorted(existing_tables),
            "missing_tables": sorted(expected_tables - existing_tables),
            "status": "ok" if expected_tables.issubset(existing_tables) else "degraded",
        }

    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _get_or_create_use_case(self, conn: sqlite3.Connection, use_case_name: str) -> int:
        row = conn.execute(
            "SELECT id FROM use_cases WHERE name = ?",
            (use_case_name,),
        ).fetchone()
        if row:
            return int(row["id"])

        cursor = conn.execute(
            "INSERT INTO use_cases (name, created_at) VALUES (?, ?)",
            (use_case_name, utc_now_iso()),
        )
        return int(cursor.lastrowid)

    def create_batch(self, use_case_name: str) -> str:
        batch_id = f"batch_{uuid4().hex}"
        with self.connection() as conn:
            use_case_id = self._get_or_create_use_case(conn, use_case_name)
            conn.execute(
                """
                INSERT INTO review_batches (id, use_case_id, status, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (batch_id, use_case_id, "pending_review", utc_now_iso()),
            )
        return batch_id

    def save_uploaded_file(self, *, batch_id: str, filename: str, file_bytes: bytes) -> str:
        safe_filename = re.sub(r"[^A-Za-z0-9._-]+", "_", filename).strip("._") or "document.bin"
        batch_dir = self.upload_storage_dir / batch_id
        batch_dir.mkdir(parents=True, exist_ok=True)
        file_path = batch_dir / safe_filename
        file_path.write_bytes(file_bytes)
        return str(file_path)

    def add_document(
        self,
        *,
        batch_id: str,
        workflow_result: dict[str, Any],
        filename: str,
        stored_file_path: str | None,
        mime_type: str | None,
        source_type: str,
    ) -> None:
        draft_fields = workflow_result.get("consolidated_fields") or workflow_result.get(
            "raw_candidate_fields",
            [],
        )
        processing_errors = workflow_result.get("processing_errors", [])
        now = utc_now_iso()

        with self.connection() as conn:
            conn.execute(
                """
                INSERT INTO documents (
                    batch_id,
                    document_id,
                    filename,
                    stored_file_path,
                    mime_type,
                    source_type,
                    document_type_guess,
                    processing_errors_json,
                    draft_fields_json,
                    final_fields_json,
                    review_status,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    batch_id,
                    workflow_result["document_id"],
                    filename,
                    stored_file_path,
                    mime_type,
                    source_type,
                    workflow_result.get("document_type_guess", ""),
                    json.dumps(processing_errors, ensure_ascii=True),
                    json.dumps(draft_fields, ensure_ascii=True),
                    json.dumps([], ensure_ascii=True),
                    "pending_review",
                    now,
                    now,
                ),
            )

    def get_batch(self, batch_id: str) -> dict[str, Any] | None:
        with self.connection() as conn:
            batch_row = conn.execute(
                """
                SELECT rb.id, rb.status, rb.created_at, rb.reviewed_at, rb.reviewed_by, uc.name AS use_case_name
                FROM review_batches rb
                JOIN use_cases uc ON uc.id = rb.use_case_id
                WHERE rb.id = ?
                """,
                (batch_id,),
            ).fetchone()
            if not batch_row:
                return None

            document_rows = conn.execute(
                """
                SELECT document_id, filename, mime_type, source_type, document_type_guess,
                       stored_file_path, processing_errors_json, draft_fields_json,
                       final_fields_json, review_status
                FROM documents
                WHERE batch_id = ?
                ORDER BY id ASC
                """,
                (batch_id,),
            ).fetchall()

        return {
            "batch_id": batch_row["id"],
            "use_case_name": batch_row["use_case_name"],
            "status": batch_row["status"],
            "created_at": batch_row["created_at"],
            "reviewed_at": batch_row["reviewed_at"],
            "reviewed_by": batch_row["reviewed_by"],
            "documents": [
                {
                    "document_id": row["document_id"],
                    "filename": row["filename"],
                    "stored_file_path": row["stored_file_path"],
                    "mime_type": row["mime_type"],
                    "source_type": row["source_type"],
                    "document_type_guess": row["document_type_guess"],
                    "processing_errors": json.loads(row["processing_errors_json"]),
                    "draft_fields": json.loads(row["draft_fields_json"]),
                    "final_fields": json.loads(row["final_fields_json"]),
                    "review_status": row["review_status"],
                }
                for row in document_rows
            ],
        }

    def export_reviewed_records(
        self,
        *,
        use_case_name: str | None = None,
        batch_id: str | None = None,
    ) -> list[dict[str, Any]]:
        query = """
            SELECT
                uc.name AS use_case_name,
                rb.id AS batch_id,
                rb.reviewed_at,
                rb.reviewed_by,
                d.document_id,
                d.filename,
                d.stored_file_path,
                d.mime_type,
                d.source_type,
                d.document_type_guess,
                d.processing_errors_json,
                d.draft_fields_json,
                d.final_fields_json
            FROM documents d
            JOIN review_batches rb ON rb.id = d.batch_id
            JOIN use_cases uc ON uc.id = rb.use_case_id
            WHERE rb.status = 'approved' AND d.review_status = 'approved'
        """
        params: list[Any] = []

        if use_case_name:
            query += " AND uc.name = ?"
            params.append(use_case_name)
        if batch_id:
            query += " AND rb.id = ?"
            params.append(batch_id)

        query += " ORDER BY rb.created_at ASC, d.id ASC"

        with self.connection() as conn:
            rows = conn.execute(query, tuple(params)).fetchall()

        return [
            {
                "schema_version": "miprov2_review_record_v1",
                "use_case_name": row["use_case_name"],
                "batch_id": row["batch_id"],
                "document_id": row["document_id"],
                "reviewed_at": row["reviewed_at"],
                "reviewed_by": row["reviewed_by"],
                "input": {
                    "filename": row["filename"],
                    "stored_file_path": row["stored_file_path"],
                    "mime_type": row["mime_type"],
                    "source_type": row["source_type"],
                    "document_type_guess": row["document_type_guess"],
                },
                "draft_fields": json.loads(row["draft_fields_json"]),
                "final_fields": json.loads(row["final_fields_json"]),
                "processing_errors": json.loads(row["processing_errors_json"]),
            }
            for row in rows
        ]

    def export_miprov2_trainset(
        self,
        *,
        use_case_name: str | None = None,
        batch_id: str | None = None,
    ) -> list[dict[str, Any]]:
        reviewed_records = self.export_reviewed_records(
            use_case_name=use_case_name,
            batch_id=batch_id,
        )

        trainset = []
        for record in reviewed_records:
            trainset.append(
                {
                    "input": {
                        "use_case_name": record["use_case_name"],
                        "document_id": record["document_id"],
                        "document_type_guess": record["input"]["document_type_guess"],
                        "source_type": record["input"]["source_type"],
                        "filename": record["input"]["filename"],
                        "stored_file_path": record["input"]["stored_file_path"],
                        "draft_fields": record["draft_fields"],
                        "processing_errors": record["processing_errors"],
                    },
                    "ideal_output": {
                        "final_fields": record["final_fields"],
                    },
                    "metadata": {
                        "schema_version": "miprov2_trainset_v1",
                        "batch_id": record["batch_id"],
                        "reviewed_at": record["reviewed_at"],
                        "reviewed_by": record["reviewed_by"],
                    },
                }
            )

        return trainset

    def submit_batch_review(
        self,
        *,
        batch_id: str,
        reviewed_by: str | None,
        documents: list[dict[str, Any]],
    ) -> None:
        now = utc_now_iso()
        with self.connection() as conn:
            for document in documents:
                conn.execute(
                    """
                    UPDATE documents
                    SET final_fields_json = ?, review_status = ?, updated_at = ?
                    WHERE batch_id = ? AND document_id = ?
                    """,
                    (
                        json.dumps(document["final_fields"], ensure_ascii=True),
                        "approved",
                        now,
                        batch_id,
                        document["document_id"],
                    ),
                )

            conn.execute(
                """
                UPDATE review_batches
                SET status = ?, reviewed_at = ?, reviewed_by = ?
                WHERE id = ?
                """,
                ("approved", now, reviewed_by, batch_id),
            )
