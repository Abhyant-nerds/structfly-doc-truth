from __future__ import annotations

import dspy


class EmailRoutingSummarySignature(dspy.Signature):
    """Summarize a commercial banking email for category routing without making the final classification."""

    email_subject = dspy.InputField(desc="Customer email subject line.")
    email_body = dspy.InputField(desc="Customer email body.")
    category_catalog = dspy.InputField(desc="Available category IDs, names, and domains.")

    primary_intent = dspy.OutputField(desc="Short description of what the customer wants.")
    business_domain = dspy.OutputField(desc="Likely banking operations domain.")
    requested_action = dspy.OutputField(desc="Action requested from the bank operations team.")
    candidate_categories = dspy.OutputField(desc="Top 2 to 4 category IDs and names.")
    evidence_phrases = dspy.OutputField(desc="Exact phrases from the email that support routing.")
    body_sufficient_for_classification = dspy.OutputField(desc="true or false.")
    routing_confidence = dspy.OutputField(desc="0.0 to 1.0.")


class EmailClassificationSignature(dspy.Signature):
    """Classify the email into exactly one commercial banking category using relevant OKF knowledge."""

    email_subject = dspy.InputField()
    email_body = dspy.InputField()
    routing_summary = dspy.InputField()
    relevant_category_knowledge = dspy.InputField()

    final_category_id = dspy.OutputField(desc="One category ID, for example CAT-002.")
    final_category_name = dspy.OutputField(desc="Exact category name.")
    confidence = dspy.OutputField(desc="0.0 to 1.0.")
    evidence = dspy.OutputField(desc="Evidence phrases from the email.")
    reason = dspy.OutputField(desc="Short reason for the selected category.")


class EmailClassificationValidationSignature(dspy.Signature):
    """Validate whether the classification is supported by the email and OKF category rules."""

    email_subject = dspy.InputField()
    email_body = dspy.InputField()
    final_category_id = dspy.InputField()
    final_category_name = dspy.InputField()
    classification_reason = dspy.InputField()
    evidence = dspy.InputField()
    relevant_category_knowledge = dspy.InputField()

    verdict = dspy.OutputField(desc="APPROVE, REJECT, or NEEDS_REVIEW.")
    validation_confidence = dspy.OutputField(desc="0.0 to 1.0.")
    reason = dspy.OutputField(desc="Why the verdict was selected.")
    retry_hint = dspy.OutputField(desc="What to improve if classification is weak.")


class EmailRoutingSummaryModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predict = dspy.ChainOfThought(EmailRoutingSummarySignature)

    def forward(self, email_subject: str, email_body: str, category_catalog: str):
        return self.predict(
            email_subject=email_subject,
            email_body=email_body,
            category_catalog=category_catalog,
        )


class EmailClassificationModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predict = dspy.ChainOfThought(EmailClassificationSignature)

    def forward(
        self,
        email_subject: str,
        email_body: str,
        routing_summary: str,
        relevant_category_knowledge: str,
    ):
        return self.predict(
            email_subject=email_subject,
            email_body=email_body,
            routing_summary=routing_summary,
            relevant_category_knowledge=relevant_category_knowledge,
        )


class EmailClassificationValidationModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predict = dspy.ChainOfThought(EmailClassificationValidationSignature)

    def forward(
        self,
        email_subject: str,
        email_body: str,
        final_category_id: str,
        final_category_name: str,
        classification_reason: str,
        evidence: str,
        relevant_category_knowledge: str,
    ):
        return self.predict(
            email_subject=email_subject,
            email_body=email_body,
            final_category_id=final_category_id,
            final_category_name=final_category_name,
            classification_reason=classification_reason,
            evidence=evidence,
            relevant_category_knowledge=relevant_category_knowledge,
        )
