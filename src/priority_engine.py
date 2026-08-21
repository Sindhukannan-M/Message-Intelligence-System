from datetime import datetime
from typing import Optional
import json
from pathlib import Path


def calculate_priority(
    deadline: Optional[datetime] = None,
    urgency: Optional[str] = None,
    category: Optional[str] = None,
    response_required: bool = False,
    sensitive: bool = False,
    status: Optional[str] = None,
    now: Optional[datetime] = None,
):
    """
    Calculate priority using multiple signals.

    Priority considers:
    - deadline proximity
    - urgency
    - message category
    - response requirement
    - sensitivity
    - current status
    """

    signals = []
    score = 0

    # --------------------------------------------------------
    # Completed / cancelled items
    # --------------------------------------------------------

    if status:
        status_lower = status.lower()

        if status_lower == "completed":
            return {
                "priority": "low",
                "reason": (
                    "The task has already been completed."
                ),
                "signals": ["completed"],
                "confidence": 0.98,
            }

        if status_lower == "cancelled":
            return {
                "priority": "low",
                "reason": (
                    "The task or event has been cancelled."
                ),
                "signals": ["cancelled"],
                "confidence": 0.98,
            }

    # --------------------------------------------------------
    # Deadline
    # --------------------------------------------------------

    if deadline and now:

        days_remaining = (
            deadline.date() - now.date()
        ).days

        if days_remaining < 0:
            score += 5
            signals.append("overdue")

        elif days_remaining == 0:
            score += 5
            signals.append("deadline_today")

        elif days_remaining == 1:
            score += 4
            signals.append("deadline_tomorrow")

        elif days_remaining <= 3:
            score += 3
            signals.append(
                "deadline_within_3_days"
            )

        elif days_remaining <= 7:
            score += 2
            signals.append(
                "deadline_within_7_days"
            )

    # --------------------------------------------------------
    # Urgency
    # --------------------------------------------------------

    if urgency:

        urgency_lower = urgency.lower()

        if urgency_lower in {
            "critical",
            "urgent",
            "immediate",
        }:

            score += 4
            signals.append(
                "urgent_language"
            )

        elif urgency_lower in {
            "high",
            "asap",
        }:

            score += 3
            signals.append(
                "high_urgency"
            )

        elif urgency_lower in {
            "medium",
            "soon",
        }:

            score += 2
            signals.append(
                "moderate_urgency"
            )

    # --------------------------------------------------------
    # Category
    # --------------------------------------------------------

    if (
        category
        and category.lower()
        == "action required"
    ):

        score += 2
        signals.append(
            "action_required"
        )

    # --------------------------------------------------------
    # Response requirement
    # --------------------------------------------------------

    if response_required:

        score += 2
        signals.append(
            "response_required"
        )

    # --------------------------------------------------------
    # Sensitivity
    # --------------------------------------------------------

    if sensitive:

        score += 2
        signals.append(
            "sensitive_information"
        )

    # --------------------------------------------------------
    # Convert score to priority
    # --------------------------------------------------------

    if score >= 7:
        priority = "critical"

    elif score >= 5:
        priority = "high"

    elif score >= 3:
        priority = "medium"

    else:
        priority = "low"

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    if len(signals) >= 3:
        confidence = 0.90

    elif len(signals) == 2:
        confidence = 0.82

    elif len(signals) == 1:
        confidence = 0.70

    else:
        confidence = 0.55

    # --------------------------------------------------------
    # Reason
    # --------------------------------------------------------

    if signals:

        reason = (
            "Priority determined using: "
            + ", ".join(signals)
            + "."
        )

    else:

        reason = (
            "No strong priority signals "
            "were identified."
        )

    return {
        "priority": priority,
        "reason": reason,
        "signals": signals,
        "confidence": confidence,
    }


# ============================================================
# L1 INPUT
# ============================================================

def load_l1_task_events(file_path: str):
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
                and isinstance(data[key], list)
            ):

                return data[key]

    raise ValueError(
        "Unable to find task/event records "
        "in L1 output."
    )


# ============================================================
# HELPERS
# ============================================================

def parse_deadline(value):
    """Safely parse a deadline."""

    if not value:
        return None

    try:

        return datetime.fromisoformat(
            str(value)
        )

    except ValueError:

        return None


def get_item_id(record):
    """
    Obtain the task/event identifier.

    Existing identifiers are preserved.
    """

    return (
        record.get("item_id")
        or record.get("task_id")
        or record.get("event_id")
        or record.get("id")
        or record.get("message_id")
    )


def get_message_id(record):
    return (
        record.get("message_id")
        or record.get("source_message_id")
    )


# ============================================================
# PRIORITY PROCESSING
# ============================================================

def process_l1_priorities(
    input_file: str,
    output_file: str,
    now: Optional[datetime] = None,
):

    """
    Apply priority processing to L1/L2 task-event records.

    Records are processed chronologically.

    When multiple messages refer to the same item, the latest
    available status, deadline, urgency, and priority signals
    are carried forward.
    """

    records = load_l1_task_events(
        input_file
    )

    # --------------------------------------------------------
    # Preserve chronological order
    # --------------------------------------------------------

    def timestamp_value(record):

        value = (
            record.get("timestamp")
            or record.get("created_at")
            or record.get("date")
        )

        if not value:
            return datetime.min

        try:
            return datetime.fromisoformat(
                str(value)
            )

        except ValueError:

            return datetime.min

    records = sorted(
        records,
        key=timestamp_value,
    )

    # Current state for each task/event.
    item_state = {}

    processed = []

    reference_now = (
        now or datetime.now()
    )

    # --------------------------------------------------------
    # Process chronologically
    # --------------------------------------------------------

    for record in records:

        item_id = get_item_id(
            record
        )

        message_id = get_message_id(
            record
        )

        previous_state = (
            item_state.get(item_id, {})
        )

        # ----------------------------------------------------
        # Read current message values
        # ----------------------------------------------------

        deadline_value = (
            record.get("deadline")
            or record.get("date")
            or record.get("due_date")
        )

        urgency = record.get(
            "urgency"
        )

        category = record.get(
            "category"
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

        # ----------------------------------------------------
        # Carry forward previous state when appropriate
        # ----------------------------------------------------

        if not deadline_value:

            deadline_value = (
                previous_state.get(
                    "deadline"
                )
            )

        if not urgency:

            urgency = (
                previous_state.get(
                    "urgency"
                )
            )

        if not category:

            category = (
                previous_state.get(
                    "category"
                )
            )

        if not status:

            status = (
                previous_state.get(
                    "status"
                )
            )

        if not response_required:

            response_required = (
                previous_state.get(
                    "response_required",
                    False,
                )
            )

        if not sensitive:

            sensitive = (
                previous_state.get(
                    "sensitive",
                    False,
                )
            )

        # ----------------------------------------------------
        # Calculate current priority
        # ----------------------------------------------------

        deadline = parse_deadline(
            deadline_value
        )

        priority_result = (
            calculate_priority(
                deadline=deadline,
                urgency=urgency,
                category=category,
                response_required=(
                    response_required
                ),
                sensitive=sensitive,
                status=status,
                now=reference_now,
            )
        )

        # ----------------------------------------------------
        # Detect updates
        # ----------------------------------------------------

        update_signals = []

        previous_deadline = (
            previous_state.get(
                "deadline"
            )
        )

        if (
            previous_deadline
            and deadline_value
            and str(previous_deadline)
            != str(deadline_value)
        ):

            update_signals.append(
                "deadline_updated"
            )

        previous_urgency = (
            previous_state.get(
                "urgency"
            )
        )

        if (
            previous_urgency
            and urgency
            and str(previous_urgency).lower()
            != str(urgency).lower()
        ):

            update_signals.append(
                "urgency_updated"
            )

        previous_status = (
            previous_state.get(
                "status"
            )
        )

        if (
            previous_status
            and status
            and str(previous_status).lower()
            != str(status).lower()
        ):

            update_signals.append(
                "status_updated"
            )

        # Add update signals to the result.
        signals = list(
            priority_result["signals"]
        )

        for signal in update_signals:

            if signal not in signals:

                signals.append(signal)

        # ----------------------------------------------------
        # Build reason
        # ----------------------------------------------------

        reason = (
            priority_result["reason"]
        )

        if update_signals:

            reason += (
                " Later chronological "
                "message updated: "
                + ", ".join(
                    update_signals
                )
                + "."
            )

        # ----------------------------------------------------
        # Build output
        # ----------------------------------------------------

        updated_record = record.copy()

        updated_record["item_id"] = (
            item_id
        )

        updated_record["message_id"] = (
            message_id
        )

        updated_record[
            "priority"
        ] = priority_result[
            "priority"
        ]

        updated_record[
            "priority_reason"
        ] = reason

        updated_record[
            "priority_signals"
        ] = signals

        updated_record[
            "priority_confidence"
        ] = priority_result[
            "confidence"
        ]

        if update_signals:

            updated_record[
                "priority_updated"
            ] = True

        else:

            updated_record[
                "priority_updated"
            ] = False

        processed.append(
            updated_record
        )

        # ----------------------------------------------------
        # Save latest state
        # ----------------------------------------------------

        item_state[item_id] = {

            "deadline": deadline_value,

            "urgency": urgency,

            "category": category,

            "status": status,

            "response_required": (
                response_required
            ),

            "sensitive": sensitive,

            "priority": (
                priority_result[
                    "priority"
                ]
            ),

            "message_id": message_id,
        }

    # --------------------------------------------------------
    # Save output
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

    results = (
        process_l1_priorities(
            input_file=input_file,
            output_file=output_file,
        )
    )

    print(
        f"Processed {len(results)} "
        "task/event records."
    )

    print(
        "Priority results saved to: "
        f"{output_file}"
    )