def build_evidence_bundle(state):
    if state.get("document_file") is not None:
        state["extracted_text"] = state.get("extracted_text", "")
    else:
        state["extracted_text"] = state.get("raw_text", "").strip()
    return state
