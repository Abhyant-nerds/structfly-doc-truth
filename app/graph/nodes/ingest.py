from uuid import uuid4

from app.core.file_utils import infer_file_metadata
from app.core.settings import get_settings


def ingest_document(state):
    settings = get_settings()
    state["document_id"] = state.get("document_id") or f"doc_{uuid4().hex}"
    if state.get("filename") and not state.get("mime_type"):
        mime_type, inferred_source_type = infer_file_metadata(state.get("filename"))
        state["mime_type"] = mime_type
        state["source_type"] = state.get("source_type") or inferred_source_type
    else:
        state["source_type"] = state.get("source_type") or settings.default_source_type
    return state
