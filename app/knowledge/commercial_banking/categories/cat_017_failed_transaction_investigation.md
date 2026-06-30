---
id: CAT-017
title: Failed Transaction Investigation
type: category
description: Customer report of a failed, returned, rejected, disputed, or debited transaction requiring investigation or reversal.
business_domain: Payments and Transfers
owner: Commercial Banking Operations
version: 1.0
status: active
tags:
  - failed transaction
  - returned payment
  - reversal
  - debited
related:
  - CAT-016
review_threshold: 0.75
---

# Failed Transaction Investigation

## Definition

Use this category when the customer reports a failed, returned, rejected, unsuccessful, or disputed transaction and asks for investigation or reversal.

## Typical Phrases

- transaction failed
- amount debited
- payment rejected
- arrange reversal
- investigate failed payment

## Required Intent

The customer should report failure or rejection and ask for investigation, reversal, or resolution.

## Boundary Rules

- Use this category when failure, rejection, return, debit without credit, dispute, investigation, or reversal language is present.
- If the customer only asks whether a payment was processed or credited, use [CAT-016 Payment Status Inquiry](/categories/cat_016_payment_status_inquiry.md).
- If the customer asks for a transaction history or account statement, use [CAT-019 Account Statement Request](/categories/cat_019_account_statement_request.md).

## Positive Examples

- NEFT failed but the amount was debited. Please investigate.

## Negative Examples

- Do not use for simple payment status checks where failure is not reported.

## Similar Categories

- [CAT-016 Payment Status Inquiry](/categories/cat_016_payment_status_inquiry.md)

## Confidence Boost Signals

High confidence when failed/rejected/returned appears with debited, reversal, or investigate.

## Evidence Expectations

Evidence should include failure and investigation or reversal wording.
