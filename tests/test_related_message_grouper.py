from src.related_message_grouper import (
    text_similarity,
    should_group,
)


def test_similar_messages():
    message_a = {
        "message": "Please submit the project report by Friday."
    }

    message_b = {
        "message": "Reminder: the project report is due Friday."
    }

    assert text_similarity(
        message_a["message"],
        message_b["message"],
    ) > 0.45


def test_unrelated_messages():
    message_a = {
        "message": "Please submit the project report."
    }

    message_b = {
        "message": "The team lunch is scheduled for tomorrow."
    }

    assert should_group(message_a, message_b) is False

def test_group_related_messages():
    from src.related_message_grouper import group_related_messages

    messages = [
        {
            "message_id": "MSG_0901",
            "message": "Please submit the project report by Friday.",
        },
        {
            "message_id": "MSG_0902",
            "message": "Reminder: the project report is due Friday.",
        },
        {
            "message_id": "MSG_0903",
            "message": "The team lunch is scheduled for tomorrow.",
        },
    ]

    groups = group_related_messages(messages)

    assert len(groups) == 2
    assert "MSG_0901" in groups[0]["message_ids"]
    assert "MSG_0902" in groups[0]["message_ids"]

def test_build_group_outputs():
    from src.related_message_grouper import build_group_outputs

    groups = [
        {
            "group_id": "GROUP_001",
            "title": "Project report",
            "messages": [
                {
                    "message_id": "MSG_0901",
                    "message": "Please submit the project report by Friday.",
                },
                {
                    "message_id": "MSG_0902",
                    "message": "Reminder: the project report is due Friday.",
                },
            ],
            "message_ids": ["MSG_0901", "MSG_0902"],
            "confidence": 0.82,
        }
    ]

    results = build_group_outputs(groups)

    assert len(results) == 1
    assert results[0]["group_id"] == "GROUP_001"
    assert results[0]["related_message_ids"] == [
        "MSG_0901",
        "MSG_0902",
    ]
    assert results[0]["status"] == "Unclear"
    assert results[0]["latest_deadline"] is None