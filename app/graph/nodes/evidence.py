def build_evidence_bundle(state):
    state["extracted_text"] = state.get("raw_text", "").strip()
    return state
