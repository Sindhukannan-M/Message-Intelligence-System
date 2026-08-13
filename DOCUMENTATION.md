# Technical Documentation

## 1. Pipeline

The system follows this processing flow:

Input CSV
→ Validate columns
→ Sort messages chronologically
→ Detect sensitive information
→ Mask sensitive information
→ Classify messages
→ Extract tasks/events
→ Assign priority
→ Generate outputs

## 2. Input Data

The input contains four fields:

- `message_id`
- `timestamp`
- `sender`
- `message`

## 3. Sensitive Information

The system checks for:

- OTPs
- Passwords
- PINs
- Bank account numbers
- Card numbers
- CVV
- Email addresses
- Phone numbers
- Home addresses

Detected values are replaced with `[MASKED]`.

## 4. Classification

Messages are classified using weighted keyword rules.

The categories are:

- Action Required
- Meeting or Event
- Personal Information
- General Information
- Promotional
- Sensitive Information

Sensitive information takes priority over normal classification.

## 5. Task and Event Extraction

The system identifies task/event signals and extracts:

- Type
- Title
- Description
- Date/deadline
- Time
- Person
- Priority
- Source message ID

Missing information is left empty rather than guessed.

## 6. Priority

Priority is determined using explicit signals.

### High

Examples include:

- urgent
- ASAP
- immediately
- critical
- important
- deadline
- must
- today

### Low

Examples include:

- optional
- no rush
- when you get a chance

Other actionable messages receive medium priority.

## 7. Output Files

The pipeline generates:

- `classification_results.csv`
- `classification_results.json`
- `task_event_results.csv`
- `task_event_results.json`
- `sensitive_results.csv`
- `sensitive_results.json`
- `mandatory_demo_results.csv`

## 8. Privacy

Raw assignment CSV files are excluded from GitHub using `.gitignore`.

Sensitive information is masked before being written to sensitive-information outputs.

## 9. Limitations

The current implementation is rule-based.

It may require additional rules for messages with ambiguous language or context-dependent meaning.

Future improvements could include supervised machine learning, embeddings, improved entity extraction, and automated evaluation metrics.