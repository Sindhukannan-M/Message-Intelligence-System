from pathlib import Path

import pandas as pd

from src.related_message_grouper import (
    group_related_messages,
    build_group_outputs,
)
from src.semantic_search import SemanticSearch
from src.state_tracker import StateTracker


L1_FILE = Path("data/l1/messages.csv")
L2_FILE = Path("data/l2/l2_messages.csv")


def load_messages():
    """Load L1 first and L2 second."""

    l1 = pd.read_csv(L1_FILE)
    l2 = pd.read_csv(L2_FILE)

    required_columns = {
        "message_id",
        "timestamp",
        "sender",
        "message",
    }

    if not required_columns.issubset(l1.columns):
        raise ValueError(
            f"L1 dataset is missing columns: "
            f"{required_columns - set(l1.columns)}"
        )

    if not required_columns.issubset(l2.columns):
        raise ValueError(
            f"L2 dataset is missing columns: "
            f"{required_columns - set(l2.columns)}"
        )

    l1["source"] = "L1"
    l2["source"] = "L2"

    l1["processing_order"] = range(
        1,
        len(l1) + 1,
    )

    l2["processing_order"] = range(
        len(l1) + 1,
        len(l1) + len(l2) + 1,
    )

    combined = pd.concat(
        [l1, l2],
        ignore_index=True,
    )

    return combined


def build_search_index(messages):
    """Build the local semantic search index."""

    documents = messages[
        [
            "message_id",
            "message",
        ]
    ].to_dict("records")

    search_engine = SemanticSearch()
    search_engine.fit(documents)

    return search_engine


def build_related_groups(messages):
    """Build related-message groups."""

    documents = messages.to_dict("records")

    groups = group_related_messages(documents)

    return build_group_outputs(groups)


def initialize_state_tracker():
    """Create the state tracker used by the L2 system."""

    return StateTracker()


def run_l2_pipeline():
    """Run the main L2 processing pipeline."""

    messages = load_messages()

    search_engine = build_search_index(messages)

    related_groups = build_related_groups(messages)

    state_tracker = initialize_state_tracker()

    return {
        "messages": messages,
        "search_engine": search_engine,
        "related_groups": related_groups,
        "state_tracker": state_tracker,
    }


if __name__ == "__main__":
    pipeline = run_l2_pipeline()

    messages = pipeline["messages"]

    print(
        f"L1 messages: "
        f"{len(messages[messages['source'] == 'L1'])}"
    )

    print(
        f"L2 messages: "
        f"{len(messages[messages['source'] == 'L2'])}"
    )

    print(
        f"Total messages: "
        f"{len(messages)}"
    )

    print(
        f"Related groups: "
        f"{len(pipeline['related_groups'])}"
    )

    print("L2 pipeline initialized successfully.")