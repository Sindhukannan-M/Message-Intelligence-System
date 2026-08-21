from datetime import datetime
from typing import Optional
import json
import re
from pathlib import Path


# ============================================================
# TEXT SIGNALS
# ============================================================

URGENT_TERMS = {
    "urgent",
    "urgently",
    "asap",
    "immediately",
    "critical",
    "emergency",
    "priority",
}

HIGH_URGENCY_TERMS = {
    "soon",
    "important",
    "high priority",
}

ACTION_TERMS = {
    "submit",
    "complete",
    "send",
    "upload",
    "reply",
    "respond",
    "fill",
    "register",
    "apply",
    "pay",
    "confirm",
    "verify",
    "finish",
    "prepare",
    "review",
    "call",
    "provide",
    "attach",
    "update",
}

RESPONSE_TERMS = {
    "reply",
    "respond",
    "confirm",
    "confirmation",
    "let me know",
    "please respond",
    "please reply",
}

HIGH_RISK_TERMS = {
    "password",
    "otp",
    "one-time password",
    "pin",
    "cvv",
    "credit card",
    "bank account",
    "authentication",
    "token",
}

COMPLETED_TERMS = {
    "completed",
    "complete",
    "finished",
    "submitted",
    "uploaded",
    "done",
    "successfully submitted",
}

CANCELLED_TERMS = {
    "cancelled",
    "canceled",
    "cancel",
}

RESCHEDULED_TERMS = {
    "rescheduled",
    "postponed",
    "moved to",
    "changed to",
    "new deadline",
    "new date",
}


# ============================================================
# HELPERS
# ============================================================

def _text(record):
    """Combine useful text fields from a task/event record."""

    fields = [
        record.get("title"),
        record.get("description"),
        record.get("message"),
        record.get("category"),
        record.get("status"),
        record.get("urgency"),
    ]

    return " ".join(
        str(value)
        for value in fields
        if value is not None
    ).lower()


def _contains_any(text, terms):
    """Return matching terms found in text."""

    return [
        term
        for term in terms
        if term in text
    ]


def _parse_date(value):
    """Parse common date formats safely."""

    if not value:
        return None

    if isinstance(value, datetime):
        return value

    value = str(value).strip()

    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
    ]

    for fmt in formats:

        try:
            return datetime.strptime(
                value,
                fmt,
            )

        except ValueError:
            continue

    try:
        return datetime.fromisoformat(
            value
        )

    except ValueError:
        return None


# ============================================================
# PRIORITY ENGINE
# ============================================================

def calculate_priority(
    deadline: Optional[datetime] = None,
    urgency: Optional[str] = None,
    category: Optional[str] = None,
    response_required: bool = False,
    sensitive: bool = False,
    status: Optional[str] = None,
    now: Optional[datetime] = None,
    text: str = "",
):
    """
    Calculate explainable priority using multiple signals.

    Signals include:
    - deadline proximity
    - overdue status
    - urgency language
    - action-required language
    - response requirement
    - sensitivity
    - task/event status

    Priority levels:
    critical, high, medium, low
    """

    now = now or datetime.now()

    text = (text or "").lower()

    signals = []
    score = 0

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    status_text = (
        str(status).lower()
        if status
        else ""
    )

    completed_match = (
        status_text in {
            "completed",
            "complete",
            "done",
            "finished",
        }
        or bool(
            _contains_any(
                text,
                COMPLETED_TERMS,
            )
        )
    )

    cancelled_match = (
        status_text in {
            "cancelled",
            "canceled",
        }
        or bool(
            _contains_any(
                text,
                CANCELLED_TERMS,
            )
        )
    )

    if completed_match:

        return {
            "priority": "low",
            "reason": (
                "The task or event has already "
                "been completed."
            ),
            "signals": [
                "completed"
            ],
            "confidence": 0.98,
        }

    if cancelled_match:

        return {
            "priority": "low",
            "reason": (
                "The task or event has been cancelled."
            ),
            "signals": [
                "cancelled"
            ],
            "confidence": 0.98,
        }

    # --------------------------------------------------------
    # DEADLINE
    # --------------------------------------------------------

    if deadline:

        days_remaining = (
            deadline.date()
            - now.date()
        ).days

        if days_remaining < 0:

            score += 6

            signals.append(
                "overdue"
            )

        elif days_remaining == 0:

            score += 6

            signals.append(
                "deadline_today"
            )

        elif days_remaining == 1:

            score += 5

            signals.append(
                "deadline_tomorrow"
            )

        elif days_remaining <= 3:

            score += 4

            signals.append(
                "deadline_within_3_days"
            )

        elif days_remaining <= 7:

            score += 3

            signals.append(
                "deadline_within_7_days"
            )

        elif days_remaining <= 14:

            score += 1

            signals.append(
                "deadline_within_14_days"
            )

    # --------------------------------------------------------
    # URGENCY FROM ACTUAL MESSAGE TEXT
    # --------------------------------------------------------

    urgent_matches = _contains_any(
        text,
        URGENT_TERMS,
    )

    high_matches = _contains_any(
        text,
        HIGH_URGENCY_TERMS,
    )

    if urgent_matches:

        score += 5

        signals.append(
            "urgent_language"
        )

    elif high_matches:

        score += 3

        signals.append(
            "high_urgency_language"
        )

    # --------------------------------------------------------
    # ACTION REQUIRED
    # --------------------------------------------------------

    action_matches = _contains_any(
        text,
        ACTION_TERMS,
    )

    if (
        action_matches
        or (
            category
            and category.lower()
            == "action required"
        )
    ):

        score += 2

        signals.append(
            "action_required"
        )

    # --------------------------------------------------------
    # RESPONSE REQUIRED
    # --------------------------------------------------------

    response_matches = _contains_any(
        text,
        RESPONSE_TERMS,
    )

    if response_required or response_matches:

        score += 2

        signals.append(
            "response_required"
        )

    # --------------------------------------------------------
    # SENSITIVE INFORMATION
    # --------------------------------------------------------

    sensitive_matches = _contains_any(
        text,
        HIGH_RISK_TERMS,
    )

    if sensitive or sensitive_matches:

        score += 2

        signals.append(
            "sensitive_information"
        )

    # --------------------------------------------------------
    # RESCHEDULE / CHANGED DEADLINE
    # --------------------------------------------------------

    rescheduled_matches = _contains_any(
        text,
        RESCHEDULED_TERMS,
    )

    if rescheduled_matches:

        score += 2

        signals.append(
            "deadline_or_schedule_changed"
        )

    # --------------------------------------------------------
    # PRIORITY MAPPING
    # --------------------------------------------------------

    if score >= 9:

        priority = "critical"

    elif score >= 6:

        priority = "high"

    elif score >= 3:

        priority = "medium"

    else:

        priority = "low"

    # --------------------------------------------------------
    # CONFIDENCE
    # --------------------------------------------------------

    signal_count = len(
        set(signals)
    )

    if signal_count >= 4:

        confidence = 0.95

    elif signal_count == 3:

        confidence = 0.90

    elif signal_count == 2:

        confidence = 0.82

    elif signal_count == 1:

        confidence = 0.70

    else:

        confidence = 0.55

    # --------------------------------------------------------
    # EXPLANATION
    # --------------------------------------------------------

    if signals:

        reason = (
            "Priority determined using: "
            + ", ".join(signals)
            + "."
        )

    else:

        reason = (
            "No strong urgency, deadline, "
            "response, sensitivity, or action "
            "signals were identified."
        )

    return {
        "priority": priority,
        "reason": reason,
        "signals": signals,
        "confidence": confidence,
    }


# ============================================================
# LOAD L1 RESULTS
# ============================================================

def load_l1_task_events(
    file_path: str,
):
    """Load task/event results generated by L1."""

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    if isinstance(data, list):

        return data

    if isinstance(data, dict):

        for key in [
            "results",
            "items",
            "tasks",
            "events",
            "data",
        ]:

            if (
                key in data
                and isinstance(
                    data[key],
                    list,
                )
            ):

                return data[key]

    raise ValueError(
        "Unable to find task/event records "
        "in L1 output."
    )


# ============================================================
# PROCESS PRIORITIES
# ============================================================

def process_l1_priorities(
    input_file: str,
    output_file: str,
    now: Optional[datetime] = None,
):
    """
    Apply priority reasoning to every L1
    task/event record.
    """

    records = load_l1_task_events(
        input_file
    )

    processed = []

    current_time = (
        now or datetime.now()
    )

    for record in records:

        # ----------------------------------------------------
        # Gather available information
        # ----------------------------------------------------

        deadline_value = (
            record.get("deadline")
            or record.get("date")
            or record.get("due_date")
            or record.get("date_or_deadline")
        )

        deadline = _parse_date(
            deadline_value
        )

        category = record.get(
            "category"
        )

        urgency = record.get(
            "urgency"
        )

        status = record.get(
            "status"
        )

        response_required = bool(
            record.get(
                "response_required",
                False,
            )
        )

        sensitive = bool(
            record.get(
                "sensitive",
                False,
            )
            or record.get(
                "is_sensitive",
                False,
            )
        )

        # IMPORTANT:
        # Build text from the actual record.
        # This fixes the previous problem where
        # urgency/action signals were missing.

        record_text = _text(
            record
        )

        # ----------------------------------------------------
        # Calculate priority
        # ----------------------------------------------------

        result = calculate_priority(
            deadline=deadline,
            urgency=urgency,
            category=category,
            response_required=response_required,
            sensitive=sensitive,
            status=status,
            now=current_time,
            text=record_text,
        )

        # ----------------------------------------------------
        # Preserve original L1 record
        # ----------------------------------------------------

        updated_record = record.copy()

        updated_record[
            "priority"
        ] = result[
            "priority"
        ]

        updated_record[
            "priority_reason"
        ] = result[
            "reason"
        ]

        updated_record[
            "priority_signals"
        ] = result[
            "signals"
        ]

        updated_record[
            "priority_confidence"
        ] = result[
            "confidence"
        ]

        updated_record[
            "priority_updated"
        ] = False

        processed.append(
            updated_record
        )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    output_path = Path(
        output_file
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            processed,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return processed


# ============================================================
# COMMAND LINE
# ============================================================

if __name__ == "__main__":

    input_file = (
        "outputs/task_event_results.json"
    )

    output_file = (
        "l2_outputs/priority_results.json"
    )

    results = process_l1_priorities(
        input_file=input_file,
        output_file=output_file,
    )

    print(
        f"Processed {len(results)} "
        "task/event records."
    )

    print(
        f"Priority results saved to: "
        f"{output_file}"
    )