from uuid import uuid4

from app.core.settings import get_settings


def ingest_document(state):
    settings = get_settings()
    state["document_id"] = state.get("document_id") or f"doc_{uuid4().hex}"
    state["source_type"] = state.get("source_type") or settings.default_source_type
    return state
