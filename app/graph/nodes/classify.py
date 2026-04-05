import logging

from app.core.llm_runtime import invoke_with_retries
from app.core.settings import get_settings
from app.dspy_modules.doc_type_classifier import DocumentTypeClassifier


logger = logging.getLogger(__name__)


def _heuristic_document_type(document_text: str) -> str:
    lowered_text = document_text.lower()
    if "invoice" in lowered_text:
        return "invoice"
    if "contract" in lowered_text or "agreement" in lowered_text:
        return "contract"
    if "resume" in lowered_text or "curriculum vitae" in lowered_text:
        return "resume"
    return "generic_document"


def _fallback_document_type(state) -> str:
    document_text = state.get("extracted_text", "")
    if document_text:
        return _heuristic_document_type(document_text)

    source_type = (state.get("source_type") or "").lower()
    if source_type == "email":
        return "email"
    if source_type == "pdf":
        return "pdf_document"
    if source_type == "word_document":
        return "word_document"
    if source_type == "spreadsheet":
        return "spreadsheet"
    return "generic_document"


def guess_document_type(state):
    document_text = state.get("extracted_text", "")
    document_file = state.get("document_file")
    classifier = DocumentTypeClassifier()
    settings = get_settings()

    pred = invoke_with_retries(
        state=state,
        stage="document_type_classification",
        invoke=lambda: classifier(
            document_text=document_text,
            document_file=document_file,
            source_type=state["source_type"],
            filename=state.get("filename", ""),
            structure_hint="basic",
        ),
        validate=lambda result: (
            bool(getattr(result, "document_type", "").strip()),
            "Expected non-empty 'document_type' in DSPy output",
        ),
        logger=logger,
        max_attempts=settings.dspy_retry_attempts,
    )

    if pred is not None:
        predicted_type = getattr(pred, "document_type", "").strip()
    else:
        predicted_type = ""

    state["document_type_guess"] = predicted_type or _fallback_document_type(state)
    return state
