def build_review_package(state):
    processing_errors = state.get("processing_errors", [])
    review_status = "approved"
    if processing_errors:
        review_status = "failed"

    state["review_package"] = {
        "document_id": state["document_id"],
        "fields": state["consolidated_fields"],
        "errors": processing_errors,
    }
    state["review_status"] = review_status
    state["reviewed_fields"] = state["consolidated_fields"]
    return state
