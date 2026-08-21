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

---

# L2 Extension

## 6. How does L2 extend L1?

L2 extends the existing L1 Message Intelligence System rather than
building a separate application.

The original 900-message L1 dataset and the structured outputs generated
by the L1 system are used as the starting point. The additional L2
messages are then processed after the L1 messages while preserving their
chronological order.

The L2 extension adds:

- Priority and action processing
- Chronological state tracking
- Related-message grouping
- Semantic retrieval and question answering
- Privacy-aware routing
- Benchmark comparison

The existing L1 classification, task/event extraction, and sensitive
information processing remain part of the application.

---

## 7. How is priority calculated and updated?

L2 assigns every actionable item one of four priority levels:

- Critical
- High
- Medium
- Low

Priority is calculated using multiple signals rather than a single
keyword.

The implemented signals include:

- Deadline proximity
- Overdue status
- Urgency
- Message category
- Response requirement
- Sensitive information
- Current task/event status

For each priority decision, the system records:

- Message ID
- Task or event ID
- Priority
- Reason
- Important signals
- Confidence score

Completed and cancelled items are handled separately so that they do
not continue to receive normal active-task priority.

The priority-processing pipeline also processes records chronologically
and maintains the latest known state for an item.

Priority results are written to:

`l2_outputs/priority_results.json`

---

## 8. How are related messages identified?

Messages that refer to the same task, event, request, or subject are
grouped using message similarity together with chronological context.

The purpose of grouping is to connect follow-ups and later updates to
earlier messages instead of treating every message as an independent
item.

A related-message group contains information such as:

- Group ID
- Group title
- Related message IDs
- Related task/event IDs
- Combined summary
- Current status
- Latest deadline
- Confidence score

The grouping output is written to:

`l2_outputs/related_groups.json`

The current grouping approach is a lightweight baseline based on
message similarity and chronological processing. It can be improved
further using stronger semantic embeddings, entity resolution, and
more explicit task/event relationships.

---

## 9. How does semantic retrieval work?

The L2 system provides local semantic-style retrieval over the combined
L1 and L2 message history.

The retrieval pipeline is:

```text
User Query
    ↓
TF-IDF representation
    ↓
Cosine similarity
    ↓
Ranked message evidence
    ↓
Answer with supporting evidence

## How does privacy-aware routing work?

The L2 system extends the existing L1 sensitive-information detection
and masking capability with privacy-aware request routing.

The routing layer evaluates whether a request contains sensitive or
high-risk information and determines how the request should be handled.

The system supports three privacy-aware behaviours:

- Local processing — the request can be processed locally without
  sending sensitive information to an external service.
- Confirmation — the request requires user confirmation before any
  external processing is allowed.
- Blocked — high-risk requests are prevented from being sent for
  external processing.

Sensitive-looking values remain masked in displayed results.

The routing decision includes the detected privacy signals and a
reason explaining why the request was assigned to a particular route.

The generated privacy-routing results are stored in:

`l2_outputs/privacy_routing_results.json`

The supplied datasets are not published to the public repository, and
sensitive-looking values are kept masked in screenshots, recordings,
logs, and hosted output.

---

## What component was optimized?

The retrieval component was optimized.

The baseline approach performs a direct sequential scan of the message
collection when searching for relevant messages.

The optimized implementation builds a local TF-IDF search index and
uses cosine similarity to rank messages against a user query.

The retrieval flow is:

```text
Messages
   ↓
TF-IDF index
   ↓
Query vector
   ↓
Cosine similarity
   ↓
Ranked relevant messages

## How was benchmarking performed?

The benchmarking compares the original retrieval approach with the
optimized retrieval approach using the same message collection and
query.

The original approach performs a direct sequential scan of the
messages. The optimized approach uses a local TF-IDF search index with
cosine-similarity ranking.

For both approaches, execution time is measured using Python's
`time.perf_counter()`.

The benchmark compares:

- Response time
- Number of retrieved results
- Result quality/overlap
- Retrieval method

The benchmark results are generated from actual local execution and
saved to:

`l2_outputs/benchmark_comparison.json`

The benchmark is intended to provide a practical comparison between
the baseline and optimized retrieval implementations. Performance
results may vary depending on the machine and execution environment.

---

## Assumptions and Limitations

### Assumptions

- The original 900 L1 messages are processed before the additional L2
  messages.
- L2 messages are processed in chronological order.
- Missing dates, people, deadlines, statuses, or events are not
  intentionally invented.
- Priority decisions are based on the available evidence and multiple
  signals.
- Later messages can update information associated with an existing
  task or event.
- Related messages are identified using message similarity together
  with chronological context.
- TF-IDF and cosine similarity are used as the local retrieval
  approach.
- Sensitive information remains masked when displayed.
- Benchmark measurements are performed locally on the development
  machine.

### Limitations

- Rule-based priority calculation may not capture every form of
  contextual urgency or importance.
- Similarity-based grouping may produce false positives or false
  negatives when related messages use substantially different wording.
- TF-IDF retrieval has more limited semantic understanding than
  embedding-based retrieval.
- Ambiguous references to people, dates, tasks, or events may remain
  unresolved.
- Natural-language deadline expressions may not always be interpreted
  correctly.
- Priority confidence scores are implementation-level confidence
  values and are not statistically calibrated probabilities.
- Sensitive-information detection depends on the patterns implemented
  by the system and may not detect every possible representation.
- Benchmark results depend on the local testing environment and should
  not be treated as universal production performance measurements.