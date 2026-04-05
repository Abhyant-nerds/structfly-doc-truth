import logging
import json

from app.dspy_modules.react_agent import DocumentDiscoveryReActAgent
from app.tools.ner import extract_named_entities
from app.tools.kv_extractor import extract_key_value_pairs


logger = logging.getLogger(__name__)


def _normalize_candidates(result):
    if isinstance(result, list):
        return result

    output = getattr(result, "output", None)
    if isinstance(output, str):
        try:
            parsed_output = json.loads(output)
        except json.JSONDecodeError:
            return []

        if isinstance(parsed_output, list):
            return parsed_output
        if isinstance(parsed_output, dict):
            return [parsed_output]
    if isinstance(output, list):
        return output
    if isinstance(output, dict):
        return [output]

    return []


def _dedupe_candidates(candidates):
    deduped_candidates = []
    seen_keys = set()

    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue

        normalized_candidate = {
            "proposed_name": str(candidate.get("proposed_name", "")).strip(),
            "raw_value": str(candidate.get("raw_value", "")).strip(),
        }
        key = (
            normalized_candidate["proposed_name"].lower(),
            normalized_candidate["raw_value"].lower(),
        )

        if not all(normalized_candidate.values()) or key in seen_keys:
            continue

        seen_keys.add(key)
        deduped_candidates.append(normalized_candidate)

    return deduped_candidates


def _merge_structured_candidates(discovered_candidates, fallback_candidates):
    explicit_candidates = [
        candidate
        for candidate in fallback_candidates
        if candidate.get("proposed_name") not in {"named_entity", "organization"}
    ]

    explicit_names = {candidate["proposed_name"].lower() for candidate in explicit_candidates}
    merged_candidates = list(explicit_candidates)

    for candidate in discovered_candidates:
        proposed_name = candidate.get("proposed_name", "").lower()
        if proposed_name in {"named_entity", "organization"} and explicit_candidates:
            continue
        if proposed_name in explicit_names:
            continue
        merged_candidates.append(candidate)

    if merged_candidates:
        return merged_candidates

    return fallback_candidates


def discover_candidate_fields(state):
    extracted_text = state.get("extracted_text", "")
    tools = [extract_named_entities, extract_key_value_pairs]
    agent = DocumentDiscoveryReActAgent(tools)
    fallback_candidates = extract_named_entities(extracted_text) + extract_key_value_pairs(
        {"text": extracted_text}
    )

    try:
        result = agent(
            document_bundle={"text": extracted_text},
            document_type_guess=state["document_type_guess"],
        )
        discovered_candidates = _normalize_candidates(result)
    except Exception:
        logger.exception("DSPy discovery failed, using deterministic fallback extractors")
        discovered_candidates = []

    state["raw_candidate_fields"] = _dedupe_candidates(
        _merge_structured_candidates(discovered_candidates, fallback_candidates)
    )
    return state
