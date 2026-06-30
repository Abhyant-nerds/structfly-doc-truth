---
id: CAT-011
title: Internet Banking Access Issue
type: category
description: Customer report of internet banking activation, login, access, or availability problems.
business_domain: User and Access Management
owner: Commercial Banking Operations
version: 1.0
status: active
tags:
  - internet banking
  - login issue
  - access issue
related:
  - CAT-012
review_threshold: 0.75
---

# Internet Banking Access Issue

## Definition

Use this category when the customer cannot access internet banking, needs activation, or reports login/access failures.

## Typical Phrases

- unable to access internet banking
- login not working
- activate net banking
- access issue

## Required Intent

The request must concern internet banking access or activation.

## Boundary Rules

- Use this category when the core issue is login failure, access failure, activation, or inability to use internet banking.
- If the customer explicitly asks to reset a password, PIN, or credential, use [CAT-012 Password Reset Request](/categories/cat_012_password_reset_request.md).
- If the issue is caused by a requested registered phone number change for OTP alerts, consider [CAT-002 Registered Phone Number Change](/categories/cat_002_registered_phone_number_change.md).

## Positive Examples

- We are unable to access internet banking.

## Negative Examples

- Do not use for explicit password reset requests.

## Similar Categories

- [CAT-012 Password Reset Request](/categories/cat_012_password_reset_request.md)

## Confidence Boost Signals

High confidence when login/access issue appears with internet banking or net banking.

## Evidence Expectations

Evidence should include internet banking access wording.
