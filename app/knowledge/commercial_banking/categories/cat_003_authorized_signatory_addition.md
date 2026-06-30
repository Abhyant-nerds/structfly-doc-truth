---
id: CAT-003
title: Authorized Signatory Addition
type: category
description: Customer request to add a new authorized signatory, signer, mandate holder, or approver to an account.
business_domain: User and Access Management
owner: Commercial Banking Operations
version: 1.0
status: active
tags:
  - authorized signatory
  - signer
  - add user
related:
  - CAT-004
  - CAT-018
review_threshold: 0.75
---

# Authorized Signatory Addition

## Definition

Use this category when the customer asks to add a new authorized signatory, signer, mandate holder, or approver for an account.

## Typical Phrases

- add authorized signatory
- add new signer
- update signing mandate
- include approver

## Required Intent

The request must ask to add a person as an authorized signer or approver.

## Boundary Rules

- Use this category when the customer wants to add or include a signer, approver, mandate holder, or authorized signatory.
- If the customer wants to remove or revoke an existing signer, use [CAT-004 Authorized Signatory Removal](/categories/cat_004_authorized_signatory_removal.md).
- If the customer is only submitting documents for an existing signer without an add request, consider [CAT-018 KYC Document Update](/categories/cat_018_kyc_document_update.md).

## Positive Examples

- Please add Mr. Rao as an authorized signatory.
- We want to include a new signer on the current account.

## Negative Examples

- Do not use for removing signatories.
- Do not use for internet banking password reset.

## Similar Categories

- [CAT-004 Authorized Signatory Removal](/categories/cat_004_authorized_signatory_removal.md)
- [CAT-018 KYC Document Update](/categories/cat_018_kyc_document_update.md)

## Confidence Boost Signals

High confidence when add/include language appears with authorized signatory, signer, mandate, or approver.

## Evidence Expectations

Evidence should name the addition request and signatory role.
