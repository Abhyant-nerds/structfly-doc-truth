import json
import logging

from app.core.llm_runtime import invoke_with_retries
from app.core.settings import get_settings
from app.dspy_modules.canonical_name_suggestion import CanonicalNameSuggestion


logger = logging.getLogger(__name__)


FIELD_SYNONYMS = {
    "invoice_no": "invoice_number",
    "invoice_num": "invoice_number",
    "inv_no": "invoice_number",
    "inv_number": "invoice_number",
    "supplier": "vendor",
    "seller": "vendor",
    "buyer": "customer",
    "client": "customer",
}


def _normalize_output(result):
    if isinstance(result, list):
        return result

    output = getattr(result, "output", None)
    if isinstance(output, str):
        try:
            parsed = json.loads(output)
        except json.JSONDecodeError:
            return []

        if isinstance(parsed, list):
            return parsed
        if isinstance(parsed, dict):
            return [parsed]
    if isinstance(output, list):
        return output
    if isinstance(output, dict):
        return [output]

    return []


def _validate_canonical_output(result):
    normalized = _normalize_output(result)
    if not isinstance(normalized, list):
        return False, "Expected canonical suggestion output to normalize to a list"

    for candidate in normalized:
        if not isinstance(candidate, dict):
            return False, "Expected every canonical suggestion candidate to be a dictionary"
        if not str(candidate.get("proposed_name", "")).strip():
            return False, "Expected every canonical suggestion to contain a non-empty proposed_name"
        if not str(candidate.get("raw_value", "")).strip():
            return False, "Expected every canonical suggestion to contain a non-empty raw_value"

    return True, None


def _deterministic_consolidation(candidates):
    consolidated = []
    seen = set()

    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue

        proposed_name = str(candidate.get("proposed_name", "")).strip().lower()
        raw_value = str(candidate.get("raw_value", "")).strip()
        if not proposed_name or not raw_value:
            continue

        canonical_name = FIELD_SYNONYMS.get(proposed_name, proposed_name)
        key = (canonical_name, raw_value.lower())
        if key in seen:
            continue

        seen.add(key)
        consolidated.append(
            {
                "proposed_name": canonical_name,
                "raw_value": raw_value,
            }
        )

    return consolidated


def consolidate_candidates(state):
    raw_candidate_fields = state.get("raw_candidate_fields", [])
    settings = get_settings()
    module = CanonicalNameSuggestion()

    result = invoke_with_retries(
        state=state,
        stage="canonical_name_suggestion",
        invoke=lambda: module(
            document_type_guess=state.get("document_type_guess", "generic_document"),
            candidate_fields_json=json.dumps(raw_candidate_fields, ensure_ascii=True),
        ),
        validate=_validate_canonical_output,
        logger=logger,
        max_attempts=settings.dspy_retry_attempts,
    )

    if result is not None:
        consolidated_fields = _normalize_output(result)
    else:
        consolidated_fields = []

    state["consolidated_fields"] = (
        _deterministic_consolidation(consolidated_fields)
        or _deterministic_consolidation(raw_candidate_fields)
    )
    return state
