from datetime import datetime, timedelta

from src.priority_engine import calculate_priority


def test_urgent_task_due_today():
    result = calculate_priority(
        deadline=datetime.now(),
        urgency="urgent",
        category="Action Required",
        response_required=True,
        now=datetime.now(),
    )

    assert result["priority"] == "critical"


def test_task_due_within_week():
    result = calculate_priority(
        deadline=datetime.now() + timedelta(days=5),
        category="Action Required",
        now=datetime.now(),
    )

    assert result["priority"] == "medium"


def test_completed_task():
    result = calculate_priority(
        status="completed"
    )

    assert result["priority"] == "low"


def test_cancelled_task():
    result = calculate_priority(
        status="cancelled"
    )

    assert result["priority"] == "low"