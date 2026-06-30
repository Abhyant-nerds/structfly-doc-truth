---
id: CAT-014
title: Beneficiary Addition
type: category
description: Customer request to add or register a new beneficiary, payee, vendor, or payment recipient.
business_domain: Payments and Transfers
owner: Commercial Banking Operations
version: 1.0
status: active
tags:
  - beneficiary
  - payee
  - add beneficiary
related:
  - CAT-015
review_threshold: 0.75
---

# Beneficiary Addition

## Definition

Use this category when the customer asks to add a new payee, beneficiary, vendor, or recipient for payments.

## Typical Phrases

- add beneficiary
- add new payee
- register vendor for payments
- add recipient

## Required Intent

The request must ask to add a beneficiary or payee.

## Boundary Rules

- Use this category when the customer wants to add, register, include, or enable a new beneficiary, payee, vendor, or recipient.
- If the customer wants to delete, remove, disable, or deactivate an existing beneficiary, use [CAT-015 Beneficiary Deletion](/categories/cat_015_beneficiary_deletion.md).
- If the customer asks to raise transfer limits for an existing beneficiary, use [CAT-013 Transaction Limit Increase](/categories/cat_013_transaction_limit_increase.md).

## Positive Examples

- Please add this supplier as a payment beneficiary.

## Negative Examples

- Do not use for deleting beneficiaries.

## Similar Categories

- [CAT-015 Beneficiary Deletion](/categories/cat_015_beneficiary_deletion.md)

## Confidence Boost Signals

High confidence when add/register language appears with beneficiary or payee.

## Evidence Expectations

Evidence should include beneficiary addition wording.
