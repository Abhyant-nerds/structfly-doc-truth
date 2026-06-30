---
id: CAT-012
title: Password Reset Request
type: category
description: Customer request to reset a password, PIN, login credential, or security credential.
business_domain: User and Access Management
owner: Commercial Banking Operations
version: 1.0
status: active
tags:
  - password reset
  - PIN reset
  - credentials
related:
  - CAT-011
review_threshold: 0.75
---

# Password Reset Request

## Definition

Use this category when the customer asks to reset password, PIN, login credentials, or security credentials.

## Typical Phrases

- reset password
- forgot password
- reset PIN
- unlock credentials

## Required Intent

The request must ask for credential reset.

## Boundary Rules

- Use this category when reset, forgot, unlock credential, PIN reset, or password reset intent is explicit.
- If the customer reports internet banking access failure without reset intent, use [CAT-011 Internet Banking Access Issue](/categories/cat_011_internet_banking_access_issue.md).
- If the customer asks to update the registered mobile number used for OTPs, use [CAT-002 Registered Phone Number Change](/categories/cat_002_registered_phone_number_change.md).

## Positive Examples

- Please reset our internet banking password.

## Negative Examples

- Do not use for general internet banking access issues without reset intent.

## Similar Categories

- [CAT-011 Internet Banking Access Issue](/categories/cat_011_internet_banking_access_issue.md)

## Confidence Boost Signals

High confidence when reset language appears with password, PIN, or credentials.

## Evidence Expectations

Evidence should include reset request wording.
