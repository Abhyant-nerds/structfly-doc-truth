from typing import Any, TypedDict

class GraphState(TypedDict, total=False):
    document_id: str
    source_type: str
    filename: str
    mime_type: str
    document_file: Any
    raw_text: str
    extracted_text: str
    document_type_guess: str
    raw_candidate_fields: list[dict[str, Any]]
    consolidated_fields: list[dict[str, Any]]
    review_fields: list[dict[str, Any]]
    review_package: dict[str, Any]
    review_status: str
    reviewed_fields: list[dict[str, Any]]
    ground_truth_record: dict[str, Any]
    processing_errors: list[dict[str, str]]
