from pathlib import Path

import pandas as pd


DEMO_FILE = Path("data/l2/l2_demo_messages.csv")


def load_demo_messages():
    """Load the unseen L2 demonstration batch."""

    df = pd.read_csv(DEMO_FILE)

    required_columns = {
        "message_id",
        "timestamp",
        "sender",
        "message",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Demo dataset is missing columns: {missing}"
        )

    return df