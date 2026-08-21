from difflib import SequenceMatcher


def text_similarity(text_a: str, text_b: str) -> float:
    """Return a simple similarity score between two messages."""

    if not text_a or not text_b:
        return 0.0

    return SequenceMatcher(
        None,
        text_a.lower(),
        text_b.lower(),
    ).ratio()


def should_group(message_a: dict, message_b: dict) -> bool:
    """
    Determine whether two messages are likely related.

    This is only the first matching layer. We will later extend
    it with task/event entities and chronology.
    """

    text_a = message_a.get("message", "")
    text_b = message_b.get("message", "")

    similarity = text_similarity(text_a, text_b)

    return similarity >= 0.45

def group_related_messages(messages, similarity_threshold=0.45):
    """
    Group chronologically ordered messages that are likely
    related to the same subject, task, or event.
    """

    groups = []

    for message in messages:
        best_group = None
        best_score = 0.0

        for group in groups:
            latest_message = group["messages"][-1]

            score = text_similarity(
                message.get("message", ""),
                latest_message.get("message", ""),
            )

            if score > best_score:
                best_score = score
                best_group = group

        if best_group is not None and best_score >= similarity_threshold:
            best_group["messages"].append(message)
            best_group["message_ids"].append(message["message_id"])
            best_group["confidence"] = round(best_score, 2)

        else:
            group_id = f"GROUP_{len(groups) + 1:03d}"

            groups.append({
                "group_id": group_id,
                "title": message.get("message", "")[:80],
                "messages": [message],
                "message_ids": [message["message_id"]],
                "confidence": 1.0,
            })

    return groups

def build_group_outputs(groups):
    """
    Convert internal groups into the structured format required
    by the L2 assignment.
    """

    results = []

    for group in groups:
        messages = group["messages"]

        message_ids = [
            message["message_id"]
            for message in messages
        ]

        # Use the latest message as the current evidence.
        latest_message = messages[-1]

        results.append({
            "group_id": group["group_id"],
            "title": group["title"],
            "related_message_ids": message_ids,
            "related_task_event_ids": [],
            "summary": latest_message.get("message", ""),
            "status": "Unclear",
            "latest_deadline": None,
            "confidence": group["confidence"],
        })

    return results

import pandas as pd
import json


def run_l2_grouping():
    """
    Run related-message grouping on the L2 message dataset.
    """

    df = pd.read_csv("data/l2/l2_messages.csv")

    messages = df.to_dict("records")

    groups = group_related_messages(messages)

    results = build_group_outputs(groups)

    with open(
        "l2_outputs/related_groups.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(f"Processed {len(messages)} L2 messages.")
    print(f"Created {len(results)} related-message groups.")
    print("Saved: l2_outputs/related_groups.json")


if __name__ == "__main__":
    run_l2_grouping()