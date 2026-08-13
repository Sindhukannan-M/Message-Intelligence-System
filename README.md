# Message Intelligence System

A lightweight message-processing system built for the AI/ML Engineer Intern assignment. The system processes messages in chronological order, classifies them, extracts useful tasks and events, and detects and protects sensitive information.

## Project Overview

The Message Intelligence System processes a collection of messages and converts unstructured message content into structured, explainable results.

The system performs three main tasks:

1. Message classification
2. Task and event extraction
3. Sensitive information detection and masking

The message-processing logic runs locally using Python and rule-based processing. Raw messages are not sent to external AI services.

---

## 1. How does message classification work?

The system classifies every message into one of six categories:

- Action Required
- Meeting or Event
- Personal Information
- General Information
- Promotional
- Sensitive Information

The classification uses a weighted keyword and rule-based approach. Each category has a set of keywords with different weights based on how strongly they indicate that category.

For example, words such as `submit`, `upload`, `deadline`, `required`, `must`, `verify`, and `confirm` provide strong signals for Action Required.

Meeting or Event messages use signals such as `meeting`, `appointment`, `interview`, `webinar`, `conference`, `workshop`, and `scheduled`.

Sensitive information is given priority when potentially sensitive data is detected.

For every message, the system stores:

- Message ID
- Predicted category
- Confidence score
- Short reason for the classification

The confidence score represents the strength of the rule-based signals. It is not a statistically calibrated machine-learning probability.

---

## 2. How are tasks and events extracted?

The system identifies messages that contain actionable tasks, reminders, meetings, or events.

Task detection uses action-related keywords such as:

- `submit`
- `complete`
- `send`
- `upload`
- `reply`
- `respond`
- `fill`
- `register`
- `apply`
- `pay`
- `confirm`
- `verify`
- `finish`
- `prepare`
- `review`
- `call`

Event detection uses keywords such as:

- `meeting`
- `appointment`
- `interview`
- `webinar`
- `conference`
- `event`
- `workshop`
- `seminar`
- `call`

For detected tasks and events, the system extracts:

- Item ID
- Type
- Title
- Description
- Date or deadline
- Time
- Person involved
- Priority
- Source message ID

The system also extracts common date and time formats when they are explicitly present.

Missing information is not guessed. If a date, time, person, or deadline cannot be confidently identified, it remains unresolved or `null`.

Priority is determined using explicit signals. Words such as `urgent`, `ASAP`, `immediately`, `critical`, `deadline`, and `must` indicate high priority, while phrases such as `optional`, `no rush`, and `when you get a chance` indicate low priority. Other cases are assigned medium priority.

---

## 3. How is sensitive information detected and masked?

Sensitive information is detected locally using predefined patterns and regular expressions.

The system checks for potentially sensitive information including:

- One-time passwords (OTPs)
- Passwords
- PINs
- Bank account numbers
- Card numbers
- CVVs
- Email addresses
- Phone numbers
- Addresses

When sensitive information is detected, the value is replaced with `[MASKED]`.

For example:

`Your OTP is 482913.`

becomes:

`Your OTP is [MASKED].`

For every detected sensitive message, the system stores:

- Message ID
- Sensitivity type
- Risk level
- Masked version of the message
- Recommended action

High-risk information such as OTPs, passwords, PINs, bank account numbers, card numbers, and CVVs is assigned a high-risk level and can receive a recommendation such as `do_not_store`.

Sensitive-looking values are not intentionally exposed in logs, screenshots, GitHub, or the video demonstration.

---

## 4. What are the assumptions and limitations?

### Assumptions

- Messages are processed in chronological order.
- The system uses information explicitly available in each message and does not invent missing details.
- If a date, time, person, or deadline cannot be confidently identified, it remains unresolved or `null`.
- Keyword matches are treated as signals rather than complete semantic understanding.
- Sensitive-information detection is pattern-based and may not identify every possible format of sensitive information.
- Classification confidence represents the strength of the implemented rule signals and is not a calibrated machine-learning probability.

### Limitations

- Rule-based classification can produce false positives or false negatives when messages use unexpected wording.
- Keyword-based classification has limited semantic understanding.
- Sensitive-information detection depends on the patterns implemented in the system.
- Unusual formats of sensitive information may not be detected.
- Person extraction may remain unresolved when a person is not clearly identified.
- Date and time extraction supports common formats but may not correctly interpret every natural-language expression.
- Confidence scores are rule-based and are not statistically calibrated.
- A trained machine-learning or NLP model could provide stronger semantic understanding and potentially improve classification and extraction accuracy.

---

## 5. AI Tool Usage Declaration

AI tool were used selectively during development to assist with:

- Error resolution
- Documentation
- Project organization
- Reviewing implementation ideas

The core message-processing logic was implemented as a local, rule-based system.

AI tool were not used to process or classify the supplied dataset, and raw messages were not sent to external AI services.