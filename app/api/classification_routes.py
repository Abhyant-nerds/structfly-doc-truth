import logging

from fastapi import APIRouter, HTTPException

from app.classification.models import EmailClassificationRequest, EmailClassificationResponse
from app.classification.pipeline import run_email_classification


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/classify-email")
def classify_email(payload: EmailClassificationRequest) -> EmailClassificationResponse:
    try:
        return run_email_classification(subject=payload.subject, body=payload.body)
    except Exception as exc:
        logger.exception("Email classification failed")
        raise HTTPException(status_code=500, detail="Email classification failed") from exc
