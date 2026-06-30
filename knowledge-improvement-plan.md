# Knowledge Improvement Plan

This plan maps the current commercial banking classification knowledge to the OKF v0.1 draft and turns the gaps into executable work.

## Scope

Current knowledge bundle:

```text
app/knowledge/commercial_banking/
|-- issue_catalog.md
`-- categories/
    |-- cat_001_registered_email_change.md
    `-- ...
```

Primary consumers:

- `app/classification/okf_loader.py`
- `app/classification/retrieval.py`
- `app/classification/pipeline.py`
- `POST /classify-email`

The current category files are already close to OKF: they are markdown files with YAML frontmatter, a `type` field, stable category IDs, tags, related categories, and structured body sections. The plan below improves conformance, discoverability, provenance, validation, and classification quality.

## Current Strengths

- Each category is a standalone markdown concept with parseable frontmatter.
- `type: category` is present, satisfying the main OKF required concept field.
- Category bodies use consistent sections: Definition, Typical Phrases, Required Intent, Positive Examples, Negative Examples, Similar Categories, Confidence Boost Signals, and Evidence Expectations.
- The classifier already retrieves focused category knowledge before final classification.
- Business-facing knowledge is versioned in Git and can be reviewed without custom tooling.

## Gaps Against OKF v0.1

| Area | Current State | OKF-Oriented Gap |
|---|---|---|
| Bundle discovery | `issue_catalog.md` lists categories by group | No root `index.md` for progressive disclosure |
| Directory discovery | `categories/` has many concepts | No `categories/index.md` |
| Update history | Git history only | No OKF `log.md` summarizing knowledge changes |
| Frontmatter | Has custom useful fields | Missing recommended `description`, `timestamp`, and optional `resource` where applicable |
| Cross-linking | `related` stores IDs only | Body does not use markdown links to related category concepts |
| Citations | No citation sections | Claims and examples have no provenance markers |
| Conformance checks | Loader is permissive | No automated validation for required fields, reserved filenames, links, duplicate IDs, or broken related references |
| Parser robustness | Custom frontmatter parser supports simple lists | Not a full YAML parser; inline lists, nested maps, quoted edge cases, and timestamps are weakly supported |
| Evaluation feedback | Samples exist in notebook data | No visible feedback loop from misclassifications into category knowledge changes |

## Target Knowledge Shape

Recommended bundle shape:

```text
app/knowledge/commercial_banking/
|-- index.md
|-- log.md
|-- issue_catalog.md
`-- categories/
    |-- index.md
    |-- cat_001_registered_email_change.md
    `-- ...
```

Recommended category frontmatter:

```yaml
---
id: CAT-001
type: Category
title: Registered Email Change
description: Customer request to update the registered email address used for banking records and communication.
business_domain: Customer Maintenance
owner: Commercial Banking Operations
version: 1.0
status: active
tags:
  - email
  - registered email
  - contact update
related:
  - CAT-002
  - CAT-005
review_threshold: 0.75
timestamp: 2026-06-30T00:00:00Z
---
```

Recommended body additions:

- Add markdown links under `## Similar Categories`, such as `[CAT-002 Registered Phone Number Change](/categories/cat_002_registered_phone_number_change.md)`.
- Add `## Boundary Rules` for categories that are commonly confused.
- Add `## Required Evidence` as a more explicit replacement or companion to Evidence Expectations.
- Add `# Citations` only when the content is backed by a source document, policy, SME review note, or evaluation finding.

## Phase 1: OKF Conformance And Navigation

Goal: make the bundle easier for humans and agents to traverse without changing classifier behavior.

Tasks:

1. Add `app/knowledge/commercial_banking/index.md`.
   - Include `okf_version: "0.1"` frontmatter as allowed by the OKF draft for bundle-root indexes.
   - Link to `issue_catalog.md` and `categories/`.
   - Describe the bundle purpose and consumers.

2. Add `app/knowledge/commercial_banking/categories/index.md`.
   - Group categories by business domain.
   - Link to each category file.
   - Include one-line descriptions once available.

3. Add `app/knowledge/commercial_banking/log.md`.
   - Use newest-first `YYYY-MM-DD` headings.
   - Record initial OKF alignment and later category changes.

4. Add `description` to every category file.
   - Keep it one sentence.
   - Use it for generated indexes, search snippets, and future UI previews.

5. Normalize `type`.
   - Decide whether to keep `type: category` or use `type: Category`.
   - Apply consistently and keep the loader tolerant of either value.

Acceptance criteria:

- Every non-reserved markdown concept has frontmatter and non-empty `type`.
- Root and category indexes let an agent discover the bundle without opening every file.
- Existing classifier still loads all 20 active categories.

## Phase 2: Relationship Quality And Boundary Clarity

Goal: reduce confusion between similar categories.

Tasks:

1. Convert `related` IDs into body links.
   - Keep `related` in frontmatter for machine use.
   - Add markdown links in `## Similar Categories` for OKF graph traversal.

2. Add `## Boundary Rules` to high-confusion pairs.
   - CAT-001 vs CAT-002: email update vs phone update.
   - CAT-003 vs CAT-004: signatory addition vs removal.
   - CAT-014 vs CAT-015: beneficiary addition vs deletion.
   - CAT-016 vs CAT-017: payment status inquiry vs failed transaction investigation.
   - CAT-011 vs CAT-012: internet banking access issue vs password reset.
   - CAT-020 vs all specific categories: fallback only when intent is not specific enough.

3. Strengthen negative examples.
   - Add at least three concrete negative examples per category.
   - Include near-miss examples that should route to a different category.

4. Add required evidence fields in prose.
   - State the minimum textual signal needed to classify into the category.
   - State what missing evidence should trigger `needs_review`.

Acceptance criteria:

- Each category links to its closest alternatives.
- Ambiguous examples are explicitly covered by boundary rules.
- Validation can use category knowledge to explain review decisions more clearly.

## Phase 3: Provenance And Review Governance

Goal: make knowledge changes auditable and safer for production use.

Tasks:

1. Add provenance metadata.
   - Recommended fields: `source`, `source_type`, `approved_by`, `approved_at`, `last_reviewed_at`.
   - Keep these producer-defined fields optional so the bundle remains OKF-compatible.

2. Add `# Citations` sections where source material exists.
   - Link to policy docs, SME notes, evaluation records, or internal references.
   - Do not invent citations when no source exists.

3. Define category lifecycle statuses.
   - Use a controlled set: `draft`, `active`, `deprecated`.
   - Make retrieval penalize or exclude non-active categories intentionally.

4. Document ownership.
   - Keep `owner` in every category.
   - Add review cadence, for example quarterly or after every evaluation failure batch.

Acceptance criteria:

- Every production category has a known owner and review status.
- Important classification rules can be traced to a source or review note.
- Knowledge changes are summarized in `log.md`.

## Phase 4: Automated Validation

Goal: catch knowledge regressions before they affect classification.

Tasks:

1. Replace or supplement the custom frontmatter parser with a real YAML parser.
   - Add `PyYAML` or use another project-approved YAML parser.
   - Preserve current behavior for existing files.

2. Add a validation command.
   - Suggested command: `uv run python -m app.classification.validate_knowledge`.
   - Validate required frontmatter fields.
   - Validate duplicate IDs.
   - Validate filename and `id` consistency.
   - Validate related IDs exist.
   - Validate markdown links that target local concepts.
   - Validate reserved `index.md` and `log.md` structure.

3. Add tests for loader and validation behavior.
   - Confirm all 20 categories load.
   - Confirm malformed frontmatter fails validation.
   - Confirm broken related references fail validation.

4. Add CI or a documented local check.
   - At minimum, document the validation command in `README.md`.

Acceptance criteria:

- A single command reports OKF conformance and taxonomy-specific issues.
- The command exits non-zero for invalid category knowledge.
- Tests cover the loader and validator.

## Phase 5: Evaluation-Driven Knowledge Improvement

Goal: connect classification outcomes back into the OKF category files.

Tasks:

1. Expand `notebooks/data/email_classification_samples.jsonl`.
   - Target at least 10 examples per category.
   - Include ambiguous and negative examples, not only easy positives.

2. Build an evaluation report.
   - Track accuracy by category.
   - Track top confusion pairs.
   - Track cases sent to review.
   - Track low-confidence but correct classifications.

3. Create a feedback workflow.
   - Misclassification found.
   - Identify whether issue is retrieval, category knowledge, prompt, or model behavior.
   - Update category examples or boundary rules.
   - Add the failed case to the evaluation set.
   - Record the change in `log.md`.

4. Tune retrieval using metadata.
   - Use `description`, `tags`, `business_domain`, and boundary rules explicitly.
   - Consider weighting `Typical Phrases`, `Required Intent`, and `Boundary Rules` differently instead of tokenizing the entire markdown uniformly.

Acceptance criteria:

- Each knowledge update is tied to an observed gap or governance need.
- Evaluation set grows with every resolved misclassification.
- Retrieval and classification quality can be measured before and after a knowledge change.

## Suggested Execution Order

1. Add indexes, log, and descriptions.
2. Add body links and boundary rules for the highest-confusion categories.
3. Add validation tooling and tests.
4. Add provenance fields and citations where real source material exists.
5. Expand evaluation samples and create the feedback loop.

## Initial Definition Of Done

The first improvement milestone is complete when:

- `index.md`, `categories/index.md`, and `log.md` exist.
- All 20 category files include `description`.
- All related category references resolve to existing category files.
- A validation command confirms OKF conformance plus taxonomy-specific checks.
- README or classification docs explain how to run the validation.
- Existing classifier behavior is unchanged except for improved retrieval context.
