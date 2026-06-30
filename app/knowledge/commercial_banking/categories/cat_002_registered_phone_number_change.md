---
id: CAT-002
title: Registered Phone Number Change
type: category
description: Customer request to update the registered phone, mobile, contact number, or OTP alert number in bank records.
business_domain: Customer Maintenance
owner: Commercial Banking Operations
version: 1.0
status: active
tags:
  - phone
  - mobile
  - contact update
  - OTP
related:
  - CAT-001
  - CAT-005
review_threshold: 0.75
---

# Registered Phone Number Change

## Definition

Use this category when the customer asks to update the registered phone number, mobile number, contact number, or official phone contact for a business or current account.

## Typical Phrases

- change mobile number
- update registered mobile
- update phone number
- new contact number
- old number is no longer active
- OTP alerts to new number

## Required Intent

The email should clearly indicate that a phone or mobile number should be changed or updated in bank records.

## Boundary Rules

- Use this category only when the requested record change is for a phone, mobile, contact, or OTP alert number.
- If the request asks to update an email address, use [CAT-001 Registered Email Change](/categories/cat_001_registered_email_change.md).
- If the request reports OTP delivery or login trouble without asking to change the registered number, consider [CAT-011 Internet Banking Access Issue](/categories/cat_011_internet_banking_access_issue.md) or review.

## Positive Examples

- Please update our registered mobile number.
- The old contact number is inactive. Kindly update the new number.

## Negative Examples

- Do not use when the customer cannot receive OTP but does not request a registered number update.
- Do not use when only an email address or address needs to be changed.

## Similar Categories

- [CAT-001 Registered Email Change](/categories/cat_001_registered_email_change.md)
- [CAT-005 Company Address Update](/categories/cat_005_company_address_update.md)
- [CAT-020 General Service Request](/categories/cat_020_general_service_request.md)

## Confidence Boost Signals

High confidence if update/change language appears with phone, mobile, contact number, or OTP alert references.

## Evidence Expectations

Evidence should include the exact phrase indicating the phone number update request.
