import logging
from typing import Any

import dspy
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.core.file_utils import infer_file_metadata, is_supported_filename
from app.graph.workflow import graph


logger = logging.getLogger(__name__)
router = APIRouter()


class IngestRequest(BaseModel):
    text: str = Field(min_length=1)
    source_type: str | None = Field(default=None, min_length=1)


class IngestResponse(BaseModel):
    document_id: str
    source_type: str
    document_type_guess: str
    review_status: str
    filename: str | None = None
    mime_type: str | None = None
    raw_candidate_fields: list[dict[str, Any]] = Field(default_factory=list)
    review_package: dict[str, Any]
    ground_truth_record: dict[str, Any]


@router.post("/ingest")
def ingest(payload: IngestRequest) -> IngestResponse:
    try:
        result = graph.invoke(
            {
                "raw_text": payload.text,
                "source_type": payload.source_type,
            }
        )
    except Exception as exc:
        logger.exception("Document ingestion failed")
        raise HTTPException(status_code=500, detail="Document ingestion failed") from exc

    return IngestResponse.model_validate(result)


@router.post("/ingest-file")
async def ingest_file(file: UploadFile = File(...)) -> IngestResponse:
    if not file.filename or not is_supported_filename(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Supported extensions are .pdf, .txt, .csv, .xlsx, .xls, .docx, and .msg",
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    mime_type, source_type = infer_file_metadata(file.filename, file.content_type)
    document_file = dspy.File.from_bytes(
        file_bytes=file_bytes,
        filename=file.filename,
        mime_type=mime_type,
    )

    try:
        result = graph.invoke(
            {
                "document_file": document_file,
                "filename": file.filename,
                "mime_type": mime_type,
                "source_type": source_type,
            }
        )
    except Exception as exc:
        logger.exception("File ingestion failed")
        raise HTTPException(status_code=500, detail="File ingestion failed") from exc

    return IngestResponse.model_validate(result)
