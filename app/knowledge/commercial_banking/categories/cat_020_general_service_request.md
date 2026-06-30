---
id: CAT-020
title: General Service Request
type: category
description: Fallback category for broad, unclear, or underspecified service requests that do not clearly match a specific category.
business_domain: Fallback
owner: Commercial Banking Operations
version: 1.0
status: active
tags:
  - general request
  - unclear
  - fallback
related:
  - CAT-001
  - CAT-002
  - CAT-005
review_threshold: 0.75
---

# General Service Request

## Definition

Use this fallback category when the customer request does not clearly match a specific category or lacks enough detail to distinguish similar categories.

## Typical Phrases

- update communication details
- service request
- update records
- please assist
- unclear request

## Required Intent

Use when the specific operational task is ambiguous or not covered by another category.

## Boundary Rules

- Use this category only when the email lacks enough evidence to choose a specific operational category.
- Do not use this category when a specific request is clearly supported by category evidence.
- If multiple specific categories are plausible and the text does not resolve the ambiguity, keep this category and mark the case for review.

## Positive Examples

- Please update our communication details, without specifying email, phone, or address.
- Please assist with our service request, without enough detail.

## Negative Examples

- Do not use when a specific category is clearly supported by evidence.

## Similar Categories

- [CAT-001 Registered Email Change](/categories/cat_001_registered_email_change.md)
- [CAT-002 Registered Phone Number Change](/categories/cat_002_registered_phone_number_change.md)
- [CAT-005 Company Address Update](/categories/cat_005_company_address_update.md)

## Confidence Boost Signals

Use when several similar categories are possible and the email lacks specific evidence.

## Evidence Expectations

Evidence should show the ambiguity or broad service request language.
