from src.state_tracker import StateTracker


def test_create_and_update_item():
    tracker = StateTracker()

    tracker.create_item(
        item_id="TASK_001",
        title="Submit report",
        source_message_id="MSG_0901",
        deadline="2026-08-25",
    )

    updated = tracker.update_item(
        item_id="TASK_001",
        message_id="MSG_0950",
        deadline="2026-08-27",
    )

    assert updated is True

    item = tracker.get_item("TASK_001")

    assert item.deadline == "2026-08-27"
    assert "MSG_0950" in item.related_message_ids


def test_status_update():
    tracker = StateTracker()

    tracker.create_item(
        item_id="TASK_002",
        title="Complete assignment",
        source_message_id="MSG_0902",
    )

    tracker.update_item(
        item_id="TASK_002",
        message_id="MSG_1000",
        status="Completed",
    )

    item = tracker.get_item("TASK_002")

    assert item.status == "Completed"