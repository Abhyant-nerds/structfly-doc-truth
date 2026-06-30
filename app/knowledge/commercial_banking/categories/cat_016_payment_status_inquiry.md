---
id: CAT-016
title: Payment Status Inquiry
type: category
description: Customer inquiry asking whether a payment, RTGS, NEFT, IMPS, or wire transfer was completed, credited, or processed.
business_domain: Payments and Transfers
owner: Commercial Banking Operations
version: 1.0
status: active
tags:
  - payment status
  - RTGS
  - NEFT
  - wire transfer
related:
  - CAT-017
review_threshold: 0.75
---

# Payment Status Inquiry

## Definition

Use this category when the customer asks whether a payment, RTGS, NEFT, IMPS, or wire transfer was completed, credited, or processed.

## Typical Phrases

- payment status
- confirm payment processed
- beneficiary has not received
- RTGS status
- NEFT status
- wire transfer status

## Required Intent

The customer should be asking for status or confirmation of a payment.

## Boundary Rules

- Use this category when the customer asks to check, confirm, trace, or report the status of a payment without clearly stating failure.
- If the customer says the transaction failed, was rejected, was returned, or needs reversal, use [CAT-017 Failed Transaction Investigation](/categories/cat_017_failed_transaction_investigation.md).
- If the customer asks to increase a payment or transfer limit, use [CAT-013 Transaction Limit Increase](/categories/cat_013_transaction_limit_increase.md).

## Positive Examples

- Please confirm whether the RTGS was successfully processed.
- The beneficiary has not confirmed receipt. Please check payment status.

## Negative Examples

- Do not use when the customer states the transaction failed and asks for investigation or reversal.

## Similar Categories

- [CAT-017 Failed Transaction Investigation](/categories/cat_017_failed_transaction_investigation.md)

## Confidence Boost Signals

High confidence when status/check/confirm language appears with payment, RTGS, NEFT, IMPS, or wire.

## Evidence Expectations

Evidence should include the status inquiry wording.
