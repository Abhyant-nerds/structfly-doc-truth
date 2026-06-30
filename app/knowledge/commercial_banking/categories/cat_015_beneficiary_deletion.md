---
id: CAT-015
title: Beneficiary Deletion
type: category
description: Customer request to delete, remove, deactivate, or disable a beneficiary, payee, vendor, or payment recipient.
business_domain: Payments and Transfers
owner: Commercial Banking Operations
version: 1.0
status: active
tags:
  - beneficiary
  - payee
  - delete beneficiary
related:
  - CAT-014
review_threshold: 0.75
---

# Beneficiary Deletion

## Definition

Use this category when the customer asks to delete, remove, deactivate, or disable a payee or beneficiary.

## Typical Phrases

- delete beneficiary
- remove payee
- deactivate recipient
- disable vendor payment

## Required Intent

The request must ask to remove a beneficiary or payee.

## Boundary Rules

- Use this category when the customer wants to delete, remove, disable, or deactivate a beneficiary, payee, vendor, or recipient.
- If the customer wants to add or register a new beneficiary, use [CAT-014 Beneficiary Addition](/categories/cat_014_beneficiary_addition.md).
- If the customer wants to revoke a human signatory or approver, use [CAT-004 Authorized Signatory Removal](/categories/cat_004_authorized_signatory_removal.md).

## Positive Examples

- Please remove this payee from our beneficiary list.

## Negative Examples

- Do not use for adding beneficiaries.

## Similar Categories

- [CAT-014 Beneficiary Addition](/categories/cat_014_beneficiary_addition.md)

## Confidence Boost Signals

High confidence when remove/delete/deactivate appears with beneficiary or payee.

## Evidence Expectations

Evidence should include beneficiary deletion wording.
