---
id: CAT-004
title: Authorized Signatory Removal
type: category
description: Customer request to remove or revoke an authorized signatory, signer, mandate holder, or approver from an account.
business_domain: User and Access Management
owner: Commercial Banking Operations
version: 1.0
status: active
tags:
  - authorized signatory
  - signer
  - remove user
related:
  - CAT-003
review_threshold: 0.75
---

# Authorized Signatory Removal

## Definition

Use this category when the customer asks to remove an authorized signatory, signer, mandate holder, or approver from an account.

## Typical Phrases

- remove authorized signatory
- delete signer
- revoke signing authority
- remove approver

## Required Intent

The request must ask to remove or revoke a person's signing authority.

## Boundary Rules

- Use this category when the customer wants to remove, delete, disable, or revoke a signatory or approver.
- If the customer wants to add a new signer, use [CAT-003 Authorized Signatory Addition](/categories/cat_003_authorized_signatory_addition.md).
- If the customer wants to delete a payment beneficiary rather than a signing authority, use [CAT-015 Beneficiary Deletion](/categories/cat_015_beneficiary_deletion.md).

## Positive Examples

- Please remove Mr. Singh as an authorized signatory.
- Revoke signing authority for the former finance manager.

## Negative Examples

- Do not use for adding new signatories.
- Do not use for deleting payment beneficiaries.

## Similar Categories

- [CAT-003 Authorized Signatory Addition](/categories/cat_003_authorized_signatory_addition.md)
- [CAT-015 Beneficiary Deletion](/categories/cat_015_beneficiary_deletion.md)

## Confidence Boost Signals

High confidence when remove/revoke/delete language appears with authorized signatory or signer.

## Evidence Expectations

Evidence should include the removal request and signatory role.
