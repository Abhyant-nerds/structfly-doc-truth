from __future__ import annotations

from typing import Any

import dspy

from app.core.file_utils import infer_file_metadata
from app.graph.workflow import graph


def process_uploaded_document(
    *,
    file_bytes: bytes,
    filename: str,
    content_type: str | None,
) -> tuple[dict[str, Any], str, str]:
    mime_type, source_type = infer_file_metadata(filename, content_type)
    document_file = dspy.File.from_bytes(
        file_bytes=file_bytes,
        filename=filename,
        mime_type=mime_type,
    )
    result = graph.invoke(
        {
            "document_file": document_file,
            "filename": filename,
            "mime_type": mime_type,
            "source_type": source_type,
        }
    )
    return result, mime_type, source_type
