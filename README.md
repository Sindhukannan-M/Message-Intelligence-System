# Message Intelligence System

An AI/ML engineering assignment project that processes fictional messages and extracts useful information while protecting sensitive data.

## What the system does

The system processes messages in chronological order and performs three main tasks:

1. Classifies each message into one of six categories.
2. Extracts actionable tasks and meetings/events.
3. Detects, masks, and assesses sensitive information.

## Message Classification

Each message is classified as one of:

- Action Required
- Meeting or Event
- Personal Information
- General Information
- Promotional
- Sensitive Information

Each classification contains:

- Message ID
- Predicted category
- Confidence score
- Reason for the decision

The current implementation uses a transparent weighted keyword/rule-based approach. This makes the decisions explainable and easy to inspect.

## Task and Event Extraction

Messages containing actionable tasks or events are processed to extract:

- Item ID
- Type
- Title
- Description
- Date/deadline
- Time
- Person involved
- Priority
- Source message ID

The system does not invent missing information. When information cannot be confidently identified, it remains unresolved/empty.

## Sensitive Information Detection

The system checks messages for potentially sensitive information such as:

- OTPs
- Passwords
- PINs
- Bank account numbers
- Card numbers
- CVV
- Email addresses
- Phone numbers
- Home addresses

Detected sensitive values are replaced with `[MASKED]` in generated sensitive-information outputs.

High-risk information is marked with a recommendation such as `do_not_store`.

## Project Structure

```text
MESSAGE_CLASSIFICATION/
├── app/
├── data/
├── outputs/
├── src/
│   ├── main.py
│   └── inspect_dataset.py
├── tests/
├── .gitignore
├── README.md
└── requirements.txt
