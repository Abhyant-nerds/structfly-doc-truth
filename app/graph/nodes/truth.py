def build_ground_truth_record(state):
    state["ground_truth_record"] = {
        "document_id": state["document_id"],
        "fields": state["reviewed_fields"],
        "errors": state.get("processing_errors", []),
    }
    return state
