def build_review_package(state):
    state["review_package"] = {
        "document_id": state["document_id"],
        "fields": state["consolidated_fields"]
    }
    state["review_status"] = "approved"
    state["reviewed_fields"] = state["consolidated_fields"]
    return state
