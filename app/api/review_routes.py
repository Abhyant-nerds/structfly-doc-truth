from __future__ import annotations

from pathlib import Path
from typing import Any

import json

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel, Field

from app.core.document_processor import process_uploaded_document
from app.core.file_utils import is_supported_filename


router = APIRouter()
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


class FinalField(BaseModel):
    field_name: str = Field(min_length=1)
    field_value: str = Field(min_length=1)


class DocumentReviewSubmission(BaseModel):
    document_id: str
    final_fields: list[FinalField] = Field(default_factory=list)


class BatchReviewSubmission(BaseModel):
    reviewed_by: str | None = None
    documents: list[DocumentReviewSubmission] = Field(default_factory=list)


@router.get("/")
def home() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@router.get("/review/{batch_id}")
def review_page(batch_id: str) -> FileResponse:
    return FileResponse(STATIC_DIR / "review.html")


@router.post("/api/review-batches")
async def create_review_batch(
    use_case_name: str = Form(...),
    files: list[UploadFile] = File(...),
):
    store = router.store
    batch_id = store.create_batch(use_case_name.strip())

    for upload in files:
        if not upload.filename or not is_supported_filename(upload.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file '{upload.filename}'.",
            )

        file_bytes = await upload.read()
        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"Uploaded file '{upload.filename}' is empty.",
            )

        try:
            stored_file_path = store.save_uploaded_file(
                batch_id=batch_id,
                filename=upload.filename,
                file_bytes=file_bytes,
            )
            result, mime_type, source_type = process_uploaded_document(
                file_bytes=file_bytes,
                filename=upload.filename,
                content_type=upload.content_type,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process file '{upload.filename}'.",
            ) from exc

        store.add_document(
            batch_id=batch_id,
            workflow_result=result,
            filename=upload.filename,
            stored_file_path=stored_file_path,
            mime_type=mime_type,
            source_type=source_type,
        )

    return {
        "batch_id": batch_id,
        "review_url": f"/review/{batch_id}",
    }


@router.get("/api/review-batches/{batch_id}")
def get_review_batch(batch_id: str) -> dict[str, Any]:
    store = router.store
    batch = store.get_batch(batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch


@router.post("/api/review-batches/{batch_id}/submit")
def submit_review_batch(batch_id: str, payload: BatchReviewSubmission) -> dict[str, str]:
    store = router.store
    batch = store.get_batch(batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")

    normalized_documents = []
    for document in payload.documents:
        normalized_documents.append(
            {
                "document_id": document.document_id,
                "final_fields": [
                    {
                        "field_name": field.field_name.strip(),
                        "field_value": field.field_value.strip(),
                    }
                    for field in document.final_fields
                    if field.field_name.strip() and field.field_value.strip()
                ],
            }
        )

    store.submit_batch_review(
        batch_id=batch_id,
        reviewed_by=payload.reviewed_by,
        documents=normalized_documents,
    )
    return {"status": "approved", "batch_id": batch_id}


@router.get("/api/training/miprov2-export.jsonl")
def export_miprov2_jsonl(
    use_case_name: str | None = Query(default=None),
    batch_id: str | None = Query(default=None),
) -> PlainTextResponse:
    store = router.store
    records = store.export_reviewed_records(
        use_case_name=use_case_name,
        batch_id=batch_id,
    )
    jsonl = "\n".join(json.dumps(record, ensure_ascii=True) for record in records)
    filename_parts = ["miprov2_export"]
    if use_case_name:
        filename_parts.append(use_case_name.replace(" ", "_"))
    if batch_id:
        filename_parts.append(batch_id)
    filename = "_".join(filename_parts) + ".jsonl"
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
    }
    return PlainTextResponse(content=jsonl, media_type="application/jsonl", headers=headers)


@router.get("/api/training/miprov2-trainset.jsonl")
def export_miprov2_trainset_jsonl(
    use_case_name: str | None = Query(default=None),
    batch_id: str | None = Query(default=None),
) -> PlainTextResponse:
    store = router.store
    records = store.export_miprov2_trainset(
        use_case_name=use_case_name,
        batch_id=batch_id,
    )
    jsonl = "\n".join(json.dumps(record, ensure_ascii=True) for record in records)
    filename_parts = ["miprov2_trainset"]
    if use_case_name:
        filename_parts.append(use_case_name.replace(" ", "_"))
    if batch_id:
        filename_parts.append(batch_id)
    filename = "_".join(filename_parts) + ".jsonl"
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
    }
    return PlainTextResponse(content=jsonl, media_type="application/jsonl", headers=headers)
