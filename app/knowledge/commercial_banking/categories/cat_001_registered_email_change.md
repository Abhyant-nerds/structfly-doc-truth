---
id: CAT-001
title: Registered Email Change
type: category
description: Customer request to update the registered email address used for banking records, alerts, statements, or communication.
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
---

# Registered Email Change

## Definition

Use this category when the customer asks to update the registered email address used for banking communication, alerts, or account records.

## Typical Phrases

- update registered email
- change email ID
- replace email address
- old email is no longer monitored
- send statements to new email

## Required Intent

The email should clearly ask the bank to change an email address in bank records.

## Boundary Rules

- Use this category only when the requested record change is for an email address.
- If the request asks to update a phone, mobile, or OTP number, use [CAT-002 Registered Phone Number Change](/categories/cat_002_registered_phone_number_change.md).
- If the request says only "communication details" without naming email, route to [CAT-020 General Service Request](/categories/cat_020_general_service_request.md) for review.

## Positive Examples

- Please update our registered email address.
- Replace the old email ID with the new finance team email.

## Negative Examples

- Do not use for mobile number changes.
- Do not use for internet banking login problems unless the customer requests an email record update.

## Similar Categories

- [CAT-002 Registered Phone Number Change](/categories/cat_002_registered_phone_number_change.md)
- [CAT-005 Company Address Update](/categories/cat_005_company_address_update.md)

## Confidence Boost Signals

High confidence when update/change language appears with email, email ID, or mailbox references.

## Evidence Expectations

Evidence should include the phrase asking to change or update the email address.
