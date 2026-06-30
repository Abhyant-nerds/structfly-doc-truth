---
id: CAT-005
title: Company Address Update
type: category
description: Customer request to update registered, mailing, office, branch, or communication address details.
business_domain: Customer Maintenance
owner: Commercial Banking Operations
version: 1.0
status: active
tags:
  - address
  - mailing address
  - office address
related:
  - CAT-001
  - CAT-002
review_threshold: 0.75
---

# Company Address Update

## Definition

Use this category when the customer asks to update registered, mailing, office, branch, or communication address details.

## Typical Phrases

- update company address
- change registered address
- new office address
- mailing address changed

## Required Intent

The request must specify an address update.

## Boundary Rules

- Use this category only when the requested record change is for a physical, registered, mailing, office, branch, or communication address.
- If the request asks to update email or phone details, use [CAT-001 Registered Email Change](/categories/cat_001_registered_email_change.md) or [CAT-002 Registered Phone Number Change](/categories/cat_002_registered_phone_number_change.md).
- If the request says only "communication details" without specifying address, email, or phone, route to [CAT-020 General Service Request](/categories/cat_020_general_service_request.md) for review.

## Positive Examples

- Please update our registered office address.
- Our mailing address has changed.

## Negative Examples

- Do not use for email or mobile number changes.
- Do not use for vague communication details unless address is specified.

## Similar Categories

- [CAT-001 Registered Email Change](/categories/cat_001_registered_email_change.md)
- [CAT-002 Registered Phone Number Change](/categories/cat_002_registered_phone_number_change.md)

## Confidence Boost Signals

High confidence when update/change language appears with address, registered office, location, or mailing details.

## Evidence Expectations

Evidence should include address update wording.
