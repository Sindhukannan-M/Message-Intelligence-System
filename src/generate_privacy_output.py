import json
from pathlib import Path

import pandas as pd

from src.privacy_router import route_request


INPUT_FILE = Path("data/l2/l2_messages.csv")
OUTPUT_FILE = Path("l2_outputs/privacy_routing_results.json")


SENSITIVE_KEYWORDS = [
    "password",
    "token",
    "credit card",
    "bank account",
    "social security",
    "authentication",
]


HIGH_RISK_KEYWORDS = [
    "password",
    "token",
    "authentication",
]


def process_privacy_routing():

    df = pd.read_csv(INPUT_FILE)

    results = []

    for _, row in df.iterrows():

        message = str(row["message"])
        message_lower = message.lower()

        contains_sensitive = any(
            keyword in message_lower
            for keyword in SENSITIVE_KEYWORDS
        )

        high_risk = any(
            keyword in message_lower
            for keyword in HIGH_RISK_KEYWORDS
        )

        result = route_request(
            contains_sensitive_data=contains_sensitive,
            sensitivity_type=(
                "sensitive_information"
                if contains_sensitive
                else None
            ),
            external_service_requested=False,
            high_risk=high_risk,
        )

        results.append({
            "message_id": row["message_id"],
            "route": result["route"],
            "signals": result["signals"],
            "reason": result["reason"],
        })

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        f"Processed {len(results)} messages."
    )

    print(
        f"Saved: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    process_privacy_routing()