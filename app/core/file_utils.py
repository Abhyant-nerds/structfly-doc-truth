from pathlib import Path


SUPPORTED_FILE_TYPES = {
    ".pdf": ("application/pdf", "pdf"),
    ".txt": ("text/plain", "text"),
    ".docx": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "word_document",
    ),
    ".msg": ("application/vnd.ms-outlook", "email"),
}


def get_extension(filename: str | None) -> str:
    return Path(filename or "").suffix.lower()


def is_supported_filename(filename: str | None) -> bool:
    return get_extension(filename) in SUPPORTED_FILE_TYPES


def infer_file_metadata(filename: str | None, content_type: str | None = None) -> tuple[str, str]:
    extension = get_extension(filename)
    default_mime_type, source_type = SUPPORTED_FILE_TYPES.get(
        extension,
        ("application/octet-stream", "binary"),
    )
    mime_type = content_type or default_mime_type
    return mime_type, source_type
