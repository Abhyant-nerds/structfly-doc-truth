from __future__ import annotations

import logging
import re
from typing import Any

from app.classification.models import CategoryCandidate, EmailClassificationResponse
from app.classification.okf_loader import get_category, load_category_knowledge, load_issue_catalog
from app.classification.retrieval import extract_category_ids, retrieve_category_candidates
from app.core.llm_runtime import invoke_with_retries
from app.core.settings import get_settings
from app.dspy_modules.email_classifier import (
    EmailClassificationModule,
    EmailClassificationValidationModule,
    EmailRoutingSummaryModule,
)


logger = logging.getLogger(__name__)
CATEGORY_ID_RE = re.compile(r"CAT-\d{3}", re.IGNORECASE)


def _prediction_to_dict(prediction: Any, fields: list[str]) -> dict[str, Any]:
    if prediction is None:
        return {}
    return {field: getattr(prediction, field, "") for field in fields}


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return max(0.0, min(1.0, float(str(value).strip())))
    except (TypeError, ValueError):
        return default


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    text = str(value).strip()
    if not text:
        return []
    if "\n" in text:
        items = [line.strip(" -,*") for line in text.splitlines()]
    else:
        items = [item.strip(" -,*") for item in text.split(",")]
    return [item for item in items if item]


def _heuristic_routing_summary(subject: str, body: str) -> dict[str, Any]:
    text = f"{subject}\n{body}".lower()
    if any(term in text for term in ["mobile", "phone", "contact number"]):
        return {
            "primary_intent": "Update registered phone or mobile number",
            "business_domain": "Customer Maintenance",
            "requested_action": "Change registered phone number",
            "candidate_categories": ["CAT-002 Registered Phone Number Change", "CAT-020 General Service Request"],
            "evidence_phrases": ["phone", "mobile", "contact number"],
            "body_sufficient_for_classification": True,
            "routing_confidence": 0.75,
        }
    if any(term in text for term in ["rtgs", "neft", "wire", "payment status", "processed"]):
        return {
            "primary_intent": "Check payment status",
            "business_domain": "Payments and Transfers",
            "requested_action": "Confirm whether payment was processed",
            "candidate_categories": ["CAT-016 Payment Status Inquiry", "CAT-017 Failed Transaction Investigation"],
            "evidence_phrases": ["payment", "processed", "beneficiary"],
            "body_sufficient_for_classification": True,
            "routing_confidence": 0.75,
        }
    return {
        "primary_intent": "General service request",
        "business_domain": "Fallback",
        "requested_action": "Review customer request",
        "candidate_categories": ["CAT-020 General Service Request"],
        "evidence_phrases": [],
        "body_sufficient_for_classification": False,
        "routing_confidence": 0.4,
    }


def _heuristic_classification(candidates: list[CategoryCandidate]) -> dict[str, Any]:
    if not candidates:
        return {
            "final_category_id": "CAT-020",
            "final_category_name": "General Service Request",
            "confidence": 0.4,
            "evidence": [],
            "reason": "No strong category candidate was found.",
        }

    top = candidates[0]
    confidence = min(0.9, max(0.45, top.score / 20.0))
    return {
        "final_category_id": top.category_id,
        "final_category_name": top.category_name,
        "confidence": confidence,
        "evidence": top.matched_terms[:5],
        "reason": f"Selected highest-scoring OKF category candidate {top.category_id}.",
    }


def _normalize_classification(raw: dict[str, Any], candidates: list[CategoryCandidate]) -> dict[str, Any]:
    category_id_match = CATEGORY_ID_RE.search(str(raw.get("final_category_id", "")))
    category_id = category_id_match.group(0).upper() if category_id_match else ""
    category_doc = get_category(category_id) if category_id else None

    if not category_doc:
        return _heuristic_classification(candidates)

    return {
        "final_category_id": category_doc.category_id,
        "final_category_name": str(raw.get("final_category_name") or category_doc.title).strip(),
        "confidence": _as_float(raw.get("confidence"), 0.0),
        "evidence": _as_list(raw.get("evidence")),
        "reason": str(raw.get("reason", "")).strip(),
    }


def _validate_result(classification: dict[str, Any], validation: dict[str, Any], candidates: list[CategoryCandidate]) -> bool:
    candidate_ids = {candidate.category_id for candidate in candidates}
    final_category_id = classification["final_category_id"]
    confidence = float(classification["confidence"])
    verdict = str(validation.get("verdict", "")).upper()

    if confidence < 0.75:
        return True
    if verdict in {"REJECT", "NEEDS_REVIEW"}:
        return True
    if final_category_id not in candidate_ids:
        return True
    if not classification.get("evidence"):
        return True
    return False


def run_email_classification(subject: str, body: str) -> EmailClassificationResponse:
    state: dict[str, Any] = {"processing_errors": []}
    settings = get_settings()
    catalog = load_issue_catalog()

    summary_module = EmailRoutingSummaryModule()
    summary_pred = invoke_with_retries(
        state=state,
        stage="email_routing_summary",
        invoke=lambda: summary_module(email_subject=subject, email_body=body, category_catalog=catalog),
        validate=lambda result: (
            bool(getattr(result, "primary_intent", "").strip()),
            "Expected non-empty primary_intent",
        ),
        logger=logger,
        max_attempts=settings.dspy_retry_attempts,
    )
    routing_summary = _prediction_to_dict(
        summary_pred,
        [
            "primary_intent",
            "business_domain",
            "requested_action",
            "candidate_categories",
            "evidence_phrases",
            "body_sufficient_for_classification",
            "routing_confidence",
        ],
    )
    if not routing_summary:
        routing_summary = _heuristic_routing_summary(subject, body)
    else:
        routing_summary["candidate_categories"] = _as_list(routing_summary.get("candidate_categories"))
        routing_summary["evidence_phrases"] = _as_list(routing_summary.get("evidence_phrases"))
        routing_summary["routing_confidence"] = _as_float(routing_summary.get("routing_confidence"), 0.0)

    candidates = retrieve_category_candidates(subject=subject, body=body, routing_summary=routing_summary)
    category_ids = [candidate.category_id for candidate in candidates]
    if not category_ids:
        category_ids = extract_category_ids(routing_summary.get("candidate_categories")) or ["CAT-020"]
    category_knowledge = load_category_knowledge(category_ids)

    classifier = EmailClassificationModule()
    classification_pred = invoke_with_retries(
        state=state,
        stage="email_classification",
        invoke=lambda: classifier(
            email_subject=subject,
            email_body=body,
            routing_summary=str(routing_summary),
            relevant_category_knowledge=category_knowledge,
        ),
        validate=lambda result: (
            bool(CATEGORY_ID_RE.search(str(getattr(result, "final_category_id", "")))),
            "Expected final_category_id like CAT-002",
        ),
        logger=logger,
        max_attempts=settings.dspy_retry_attempts,
    )
    classification = _normalize_classification(
        _prediction_to_dict(
            classification_pred,
            ["final_category_id", "final_category_name", "confidence", "evidence", "reason"],
        ),
        candidates,
    )

    validator = EmailClassificationValidationModule()
    validation_pred = invoke_with_retries(
        state=state,
        stage="email_classification_validation",
        invoke=lambda: validator(
            email_subject=subject,
            email_body=body,
            final_category_id=classification["final_category_id"],
            final_category_name=classification["final_category_name"],
            classification_reason=classification["reason"],
            evidence=str(classification["evidence"]),
            relevant_category_knowledge=category_knowledge,
        ),
        validate=lambda result: (
            str(getattr(result, "verdict", "")).upper() in {"APPROVE", "REJECT", "NEEDS_REVIEW"},
            "Expected validation verdict APPROVE, REJECT, or NEEDS_REVIEW",
        ),
        logger=logger,
        max_attempts=settings.dspy_retry_attempts,
    )
    validation = _prediction_to_dict(
        validation_pred,
        ["verdict", "validation_confidence", "reason", "retry_hint"],
    )
    if not validation:
        validation = {
            "verdict": "NEEDS_REVIEW" if classification["confidence"] < 0.75 else "APPROVE",
            "validation_confidence": classification["confidence"],
            "reason": "Fallback validation based on deterministic confidence and retrieval checks.",
            "retry_hint": "",
        }
    validation["validation_confidence"] = _as_float(validation.get("validation_confidence"), 0.0)

    needs_review = _validate_result(classification, validation, candidates)

    return EmailClassificationResponse(
        final_category_id=classification["final_category_id"],
        final_category_name=classification["final_category_name"],
        confidence=round(float(classification["confidence"]), 3),
        needs_review=needs_review,
        routing_summary=routing_summary,
        candidates=candidates,
        evidence=classification["evidence"],
        reason=classification["reason"],
        validation=validation,
        processing_errors=state["processing_errors"],
    )
