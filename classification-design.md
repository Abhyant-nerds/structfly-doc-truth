# Commercial Email Classification Design

This document explains the commercial banking email classification module added to the repo.

## 1. Goal

Classify long commercial banking customer emails into operational categories, with enough evidence to explain:

- what the customer is asking
- which categories were considered
- which OKF files were used
- why the final category was selected
- whether the case needs review

The module is a POC beside the existing document ground-truth workflow. It does not replace the current LangGraph document ingestion and review pipeline.

## 2. Main Files

```text
app/
├── api/
│   └── classification_routes.py
├── classification/
│   ├── __init__.py
│   ├── models.py
│   ├── okf_loader.py
│   ├── retrieval.py
│   ├── pipeline.py
│   └── evaluation.py
├── dspy_modules/
│   └── email_classifier.py
└── knowledge/
    └── commercial_banking/
        ├── issue_catalog.md
        └── categories/
            ├── cat_001_registered_email_change.md
            ├── cat_002_registered_phone_number_change.md
            └── ...
```

Testing files:

```text
notebooks/
├── email_classification_poc_testing.ipynb
└── data/
    └── email_classification_samples.jsonl
```

## 3. API Surface

Route:

```text
POST /classify-email
```

Request:

```json
{
  "subject": "Change of registered mobile number",
  "body": "Please update the registered mobile number for our current account."
}
```

Response:

```json
{
  "final_category_id": "CAT-002",
  "final_category_name": "Registered Phone Number Change",
  "confidence": 0.9,
  "needs_review": false,
  "routing_summary": {},
  "candidates": [],
  "evidence": [],
  "reason": "...",
  "validation": {},
  "processing_errors": []
}
```

## 4. OKF Knowledge Design

OKF means Open Knowledge File style in this repo: business knowledge is stored in markdown files with simple front matter.

Catalog:

```text
app/knowledge/commercial_banking/issue_catalog.md
```

Category files:

```text
app/knowledge/commercial_banking/categories/cat_002_registered_phone_number_change.md
```

Each category file has front matter:

```markdown
---
id: CAT-002
title: Registered Phone Number Change
type: category
business_domain: Customer Maintenance
owner: Commercial Banking Operations
version: 1.0
status: active
tags:
  - phone
  - mobile
  - contact update
related:
  - CAT-001
  - CAT-005
review_threshold: 0.75
---
```

And body sections:

- Definition
- Typical Phrases
- Required Intent
- Positive Examples
- Negative Examples
- Similar Categories
- Confidence Boost Signals
- Evidence Expectations

Why this is useful:

- category rules are versioned in Git
- business users can review markdown
- retrieval can search tags and phrases
- Qwen receives focused category knowledge instead of one giant prompt
- responses can show which category files were used

## 5. Category Set

The POC includes 20 categories:

| ID | Category |
|---|---|
| CAT-001 | Registered Email Change |
| CAT-002 | Registered Phone Number Change |
| CAT-003 | Authorized Signatory Addition |
| CAT-004 | Authorized Signatory Removal |
| CAT-005 | Company Address Update |
| CAT-006 | Company Name Change |
| CAT-007 | Account Closure Request |
| CAT-008 | Account Opening Status Inquiry |
| CAT-009 | Cheque Book Request |
| CAT-010 | Debit Card Request |
| CAT-011 | Internet Banking Access Issue |
| CAT-012 | Password Reset Request |
| CAT-013 | Transaction Limit Increase |
| CAT-014 | Beneficiary Addition |
| CAT-015 | Beneficiary Deletion |
| CAT-016 | Payment Status Inquiry |
| CAT-017 | Failed Transaction Investigation |
| CAT-018 | KYC Document Update |
| CAT-019 | Account Statement Request |
| CAT-020 | General Service Request |

## 6. Runtime Flow

```text
Email subject + body
      |
      v
DSPy routing summary
      |
      v
Local OKF retrieval
      |
      v
Load top category markdown files
      |
      v
DSPy final classification
      |
      v
DSPy validation
      |
      v
Review rules and response
```

### High-Level Flow Explanation

The classifier does not ask Qwen to classify a long email directly in one step. It first converts the email into a routing artifact, then retrieves the most relevant OKF category files, then asks Qwen to classify using only that focused knowledge.

Example input:

```json
{
  "subject": "Change of registered mobile number",
  "body": "Hello Team, our finance manager has changed his mobile number. Please update the registered mobile number for our current account with immediate effect. The old number should no longer be used for OTP alerts or banking communication."
}
```

#### Step 1: Routing Summary

The first DSPy/Qwen stage extracts the operational intent without making the final decision.

Expected routing summary:

```json
{
  "primary_intent": "Update registered mobile number",
  "business_domain": "Customer Maintenance",
  "requested_action": "Change registered phone number",
  "candidate_categories": [
    "CAT-002 Registered Phone Number Change",
    "CAT-020 General Service Request"
  ],
  "evidence_phrases": [
    "changed his mobile number",
    "update the registered mobile number",
    "old number should no longer be used for OTP alerts"
  ],
  "body_sufficient_for_classification": true,
  "routing_confidence": 0.9
}
```

Why this step exists:

- long emails can contain signatures, history, and extra context
- the classifier needs the actual requested action
- downstream retrieval can use `business_domain`, `requested_action`, evidence phrases, and candidate category IDs

#### Step 2: Local OKF Retrieval

The retrieval layer searches local OKF category files using:

- email subject
- email body
- `primary_intent`
- `requested_action`
- `business_domain`
- evidence phrases
- candidate category IDs

Expected top candidates:

```json
[
  {
    "category_id": "CAT-002",
    "category_name": "Registered Phone Number Change",
    "source_file": "knowledge/commercial_banking/categories/cat_002_registered_phone_number_change.md",
    "matched_terms": ["mobile", "number", "registered", "update", "OTP"]
  },
  {
    "category_id": "CAT-001",
    "category_name": "Registered Email Change",
    "source_file": "knowledge/commercial_banking/categories/cat_001_registered_email_change.md",
    "matched_terms": ["registered", "update"]
  },
  {
    "category_id": "CAT-005",
    "category_name": "Company Address Update",
    "source_file": "knowledge/commercial_banking/categories/cat_005_company_address_update.md",
    "matched_terms": ["update", "communication"]
  }
]
```

Why this step exists:

- Qwen receives only relevant category rules, not all business knowledge
- the system can explain which OKF files were considered
- candidate recall can be measured separately from final accuracy

#### Step 3: Load Relevant OKF Files

The pipeline loads full markdown for the top candidates, especially:

```text
app/knowledge/commercial_banking/categories/cat_002_registered_phone_number_change.md
```

That file contains:

- definition
- typical phrases
- required intent
- positive examples
- negative examples
- similar categories
- evidence expectations

This gives Qwen specific business rules such as:

```text
Use this category when the customer asks to update the registered phone number, mobile number, contact number, or official phone contact.
```

#### Step 4: Final Classification

The final DSPy/Qwen classifier receives:

- original email subject/body
- routing summary
- relevant OKF markdown

Expected final classification:

```json
{
  "final_category_id": "CAT-002",
  "final_category_name": "Registered Phone Number Change",
  "confidence": 0.94,
  "evidence": [
    "update the registered mobile number",
    "old number should no longer be used for OTP alerts"
  ],
  "reason": "The customer explicitly asks the bank to update the registered mobile number for the current account."
}
```

Why this step exists:

- the model makes the final business decision
- the decision is grounded in OKF rules
- the output includes evidence and reason for auditability

#### Step 5: Validation

The validator checks whether the final classification is supported by the email and OKF rules.

Expected validation:

```json
{
  "verdict": "APPROVE",
  "validation_confidence": 0.95,
  "reason": "The selected category matches the explicit registered mobile number update request.",
  "retry_hint": ""
}
```

If the email said only "update communication details" without specifying phone, email, or address, the validator should return:

```text
NEEDS_REVIEW
```

#### Step 6: Final Response

The API returns a single structured response:

```json
{
  "final_category_id": "CAT-002",
  "final_category_name": "Registered Phone Number Change",
  "confidence": 0.94,
  "needs_review": false,
  "routing_summary": {},
  "candidates": [],
  "evidence": [
    "update the registered mobile number"
  ],
  "reason": "The customer explicitly asks to update the registered mobile number.",
  "validation": {
    "verdict": "APPROVE"
  },
  "processing_errors": []
}
```

The important design point is that every final decision has a trace:

```text
email evidence -> routing summary -> OKF candidates -> category markdown -> final classification -> validation
```

## 7. DSPy Modules

File:

```text
app/dspy_modules/email_classifier.py
```

Modules:

- `EmailRoutingSummaryModule`
- `EmailClassificationModule`
- `EmailClassificationValidationModule`

Signatures:

- `EmailRoutingSummarySignature`
- `EmailClassificationSignature`
- `EmailClassificationValidationSignature`

The model is configured globally by existing app startup:

```python
dspy.configure(lm=lm)
```

Default provider:

```text
ollama_chat
```

Model comes from:

```env
DSPY_MODEL=<model>
```

## 8. Retrieval Design

File:

```text
app/classification/retrieval.py
```

Retrieval is local and deterministic for v1. There is no vector database yet.

Inputs:

- email subject
- email body
- routing summary
- candidate category IDs from the routing model

Scoring uses:

- title/tag keyword overlap
- markdown content overlap
- routing candidate ID boost
- business domain boost
- active status check

Output:

```python
list[CategoryCandidate]
```

Each candidate includes:

- `category_id`
- `category_name`
- `score`
- `source_file`
- `matched_terms`

## 9. Pipeline Design

File:

```text
app/classification/pipeline.py
```

Main entrypoint:

```python
run_email_classification(subject: str, body: str)
```

Steps:

1. Load OKF issue catalog.
2. Run DSPy routing summary.
3. Fall back to heuristic routing if DSPy fails.
4. Retrieve top OKF category candidates.
5. Load full markdown for selected categories.
6. Run DSPy final classifier.
7. Fall back to top retrieval candidate if DSPy fails.
8. Run DSPy validator.
9. Apply deterministic review rules.
10. Return `EmailClassificationResponse`.

## 10. Review Rules

`needs_review = true` when:

- confidence is below `0.75`
- validator returns `REJECT`
- validator returns `NEEDS_REVIEW`
- final category is not in retrieved candidates
- evidence is missing

These rules keep ambiguous requests from being silently auto-approved.

## 11. Fallback Behavior

The module intentionally returns a structured response even when Ollama is unavailable.

If DSPy/Qwen fails:

- routing uses simple heuristics
- classification uses the highest-scoring retrieved OKF candidate
- validation uses deterministic confidence checks
- `processing_errors` records the failed DSPy stage

This makes local debugging easier, but a clean LLM test should have:

```text
processing_errors = []
```

## 12. Google Knowledge Catalog Pattern Adaptation

The referenced Google Knowledge Catalog discovery pattern is adapted as:

| Discovery idea | This module |
|---|---|
| Break request into search operations | Routing summary extracts intent/action/domain |
| Generate query variants | Retrieval uses subject, body, intent, action, evidence, and candidate IDs |
| Retrieve in batches | Local category markdown files are searched |
| Deduplicate and rank | Candidates are scored and sorted |
| Return auditable evidence | Response includes candidates, source files, matched terms, evidence, and reason |

## 13. Evaluation Design

Notebook:

```text
notebooks/email_classification_poc_testing.ipynb
```

Data:

```text
notebooks/data/email_classification_samples.jsonl
```

Evaluation helper:

```text
app/classification/evaluation.py
```

Metrics:

- final category accuracy
- candidate recall
- review behavior

Most important early metric:

```text
candidate_recall
```

If the expected category is not retrieved, improve the OKF file before tuning the LLM prompts.

## 14. Current Limitations

- Attachments are not classified.
- Retrieval is keyword-based, not vector-based.
- Category front matter parser supports only the simple schema currently used.
- No persistence of classification results yet.
- No human review UI integration for low-confidence email classifications yet.
- No DSPy optimization/few-shot training yet.

## 15. Future Scope

Recommended next steps:

1. Add more labeled email samples, targeting 50-100 examples.
2. Tune OKF tags and typical phrases based on candidate recall.
3. Add tests for loader, retrieval, and review rules.
4. Add vector search over OKF markdown after keyword retrieval is stable.
5. Persist `needs_review` classifications into the existing SQLite review workflow.
6. Add UI support for reviewing email classification decisions.
7. Add attachment-aware classification.
8. Add DSPy optimization using reviewed examples.
9. Add category versioning and release metadata.
10. Add dashboards for category accuracy, false positives, and review rate.

## 16. When to Edit OKF vs Code

Edit OKF markdown when:

- the category definition is unclear
- common phrases are missing
- examples are weak
- similar categories need clearer separation
- retrieval does not include the expected category

Edit code when:

- scoring logic needs a new signal
- response shape changes
- review rules change
- new persistence or UI integration is needed
- model invocation behavior changes
