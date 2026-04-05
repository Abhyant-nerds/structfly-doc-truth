def consolidate_candidates(state):
    state["consolidated_fields"] = state.get("raw_candidate_fields", [])
    return state
