import logging

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


def guess_document_type(state):
    document_text = state.get("extracted_text", "")
    classifier = DocumentTypeClassifier()

    try:
        pred = classifier(
            document_text=document_text,
            source_type=state["source_type"],
            structure_hint="basic",
        )
        predicted_type = getattr(pred, "document_type", "").strip()
    except Exception:
        logger.exception("DSPy document classification failed, using heuristic fallback")
        predicted_type = ""

    state["document_type_guess"] = predicted_type or _heuristic_document_type(document_text)
    return state
