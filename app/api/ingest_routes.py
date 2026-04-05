import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

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
