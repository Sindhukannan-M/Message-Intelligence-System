import re
import json
from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = ROOT / "data" / "messages.csv"
MANDATORY_PATH = ROOT / "data" / "mandatory_demo_ids.csv"
OUTPUT_DIR = ROOT / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================
# LOAD AND VALIDATE DATA
# ============================================================

df = pd.read_csv(DATA_PATH)

REQUIRED_COLUMNS = {
    "message_id",
    "timestamp",
    "sender",
    "message"
}

missing_columns = REQUIRED_COLUMNS - set(df.columns)

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

# Process chronologically as required by the assignment
df["timestamp_parsed"] = pd.to_datetime(
    df["timestamp"],
    dayfirst=True,
    errors="coerce"
)

df = df.sort_values(
    by=["timestamp_parsed", "message_id"]
).reset_index(drop=True)

print(f"Loaded {len(df)} messages.")


# ============================================================
# 1. SENSITIVE INFORMATION DETECTION
# ============================================================

SENSITIVE_PATTERNS = {

    "one_time_password": [
        r"\b(?:otp|one[- ]time password|verification code)"
        r"\D{0,20}\d{4,8}\b"
    ],

    "password": [
        r"\b(?:password|passcode)"
        r"\s*(?:is|:|=)\s*\S+"
    ],

    "pin": [
        r"\b(?:pin|security pin)"
        r"\D{0,10}\d{4,8}\b"
    ],

    "bank_account": [
        r"\b(?:account number|account no\.?|bank account)"
        r"\D{0,15}\d{8,18}\b"
    ],

    "card_number": [
        r"\b(?:\d[ -]?){13,19}\b"
    ],

    "cvv": [
        r"\b(?:cvv|cvc)"
        r"\D{0,10}\d{3,4}\b"
    ],

    "email_address": [
        r"\b[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    ],

    "phone_number": [
        r"(?<!\d)"
        r"(?:\+91[-\s]?)?[6-9]\d{9}"
        r"(?!\d)"
    ],

    "home_address": [
        r"\b\d{1,5}\s+"
        r"[A-Za-z0-9\s]+"
        r"(?:street|st|road|rd|avenue|ave|"
        r"lane|ln|nagar|layout)\b"
    ]
}


HIGH_RISK_TYPES = {
    "one_time_password",
    "password",
    "pin",
    "bank_account",
    "card_number",
    "cvv"
}


def detect_sensitive(text):
    """
    Detect sensitive information and return a masked version.

    The original sensitive value is never returned in the
    generated sensitive-information output.
    """

    original_text = str(text)
    masked_text = original_text
    detected_types = []

    for sensitivity_type, patterns in SENSITIVE_PATTERNS.items():

        for pattern in patterns:

            if re.search(
                pattern,
                masked_text,
                flags=re.IGNORECASE
            ):

                if sensitivity_type not in detected_types:
                    detected_types.append(sensitivity_type)

                masked_text = re.sub(
                    pattern,
                    "[MASKED]",
                    masked_text,
                    flags=re.IGNORECASE
                )

    if not detected_types:

        return {
            "is_sensitive": False,
            "sensitivity_type": None,
            "risk": None,
            "masked_text": original_text,
            "recommended_action": None
        }

    if any(
        item in HIGH_RISK_TYPES
        for item in detected_types
    ):
        risk = "high"
        action = "do_not_store"

    else:
        risk = "medium"
        action = "safe_to_process_locally"

    return {
        "is_sensitive": True,
        "sensitivity_type": ", ".join(detected_types),
        "risk": risk,
        "masked_text": masked_text,
        "recommended_action": action
    }


# ============================================================
# 2. MESSAGE CLASSIFICATION
# ============================================================

CATEGORY_RULES = {

    "action_required": {
        "submit": 3,
        "complete": 2,
        "send": 2,
        "upload": 3,
        "reply": 3,
        "respond": 3,
        "review": 2,
        "fill": 2,
        "register": 2,
        "apply": 2,
        "pay": 3,
        "verify": 2,
        "confirm": 2,
        "required": 3,
        "deadline": 3,
        "due": 3,
        "must": 3,
        "need to": 3,
        "please": 1
    },

    "meeting_or_event": {
        "meeting": 5,
        "appointment": 5,
        "interview": 5,
        "webinar": 4,
        "conference": 4,
        "workshop": 4,
        "seminar": 4,
        "event": 4,
        "catch-up": 4,
        "call": 3,
        "scheduled": 3,
        "calendar": 2,
        "dinner": 3
    },

    "personal_information": {
        "birthday": 4,
        "date of birth": 5,
        "dob": 5,
        "personal details": 4,
        "personal information": 4
    },

    "promotional": {
        "discount": 4,
        "offer": 3,
        "sale": 4,
        "coupon": 4,
        "promo": 4,
        "promotion": 4,
        "deal": 3,
        "limited time": 4,
        "cashback": 3,
        "shop now": 4,
        "buy now": 4,
        "exclusive": 3,
        "subscribe": 3
    },

    "general_information": {
        "fyi": 3,
        "update": 2,
        "announcement": 3,
        "information": 2,
        "notice": 2,
        "reminder": 1,
        "status": 2,
        "notification": 2,
        "regarding": 1
    }
}


def classify_message(text, sensitive_result):

    text_lower = str(text).lower()

    # Security/privacy information has highest priority.
    if sensitive_result["is_sensitive"]:

        return {
            "category": "sensitive_information",
            "confidence": 0.98,
            "reason": (
                "The message contains potentially sensitive "
                "personal or security information."
            )
        }

    scores = {}

    for category, keywords in CATEGORY_RULES.items():

        score = 0

        for keyword, weight in keywords.items():

            if keyword in text_lower:
                score += weight

        scores[category] = score

    max_score = max(scores.values())

    if max_score == 0:

        return {
            "category": "general_information",
            "confidence": 0.45,
            "reason": (
                "No strong category-specific signal "
                "was detected."
            )
        }

    ranked = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    best_category = ranked[0][0]
    best_score = ranked[0][1]
    second_score = ranked[1][1]

    total_score = sum(scores.values())

    confidence = best_score / total_score

    # Reduce confidence when categories compete closely.
    if best_score == second_score:
        confidence = 0.55

    elif best_score - second_score == 1:
        confidence = min(confidence, 0.70)

    confidence = round(
        max(0.40, min(confidence, 0.95)),
        2
    )

    matched_keywords = []

    for keyword in CATEGORY_RULES[best_category]:

        if keyword in text_lower:
            matched_keywords.append(keyword)

    matched_keywords = matched_keywords[:3]

    reason = (
        f"Detected signals related to "
        f"{best_category.replace('_', ' ')}"
    )

    if matched_keywords:
        reason += (
            f": {', '.join(matched_keywords)}."
        )

    return {
        "category": best_category,
        "confidence": confidence,
        "reason": reason
    }


# ============================================================
# 3. DATE EXTRACTION
# ============================================================

def extract_date(text):

    text = str(text)

    # Explicit YYYY-MM-DD
    match = re.search(
        r"\b(20\d{2})[-/](\d{1,2})[-/](\d{1,2})\b",
        text
    )

    if match:

        year, month, day = match.groups()

        return (
            f"{year}-{int(month):02d}-{int(day):02d}"
        )

    return None


# ============================================================
# 4. TIME EXTRACTION
# ============================================================

def extract_time(text):

    text = str(text)

    # 12-hour format
    match = re.search(
        r"\b(?:at\s+)?"
        r"(1[0-2]|0?[1-9])"
        r"(?::([0-5]\d))?"
        r"\s*(AM|PM|am|pm)\b",
        text
    )

    if match:

        hour = match.group(1)
        minute = match.group(2) or "00"
        period = match.group(3).upper()

        return f"{hour}:{minute} {period}"

    # 24-hour format
    match = re.search(
        r"\b([01]\d|2[0-3]):([0-5]\d)\b",
        text
    )

    if match:
        return match.group(0)

    return None


# ============================================================
# 5. TASK / EVENT DETECTION
# ============================================================

TASK_RULES = [
    "submit",
    "complete",
    "send",
    "upload",
    "reply",
    "respond",
    "review",
    "fill",
    "register",
    "apply",
    "pay",
    "confirm",
    "verify",
    "prepare",
    "finish"
]

EVENT_RULES = [
    "meeting",
    "appointment",
    "interview",
    "webinar",
    "conference",
    "workshop",
    "seminar",
    "event",
    "catch-up",
    "call",
    "dinner"
]


def determine_priority(text):

    text_lower = str(text).lower()

    high_signals = [
        "urgent",
        "asap",
        "immediately",
        "critical",
        "important",
        "deadline",
        "must",
        "today"
    ]

    low_signals = [
        "optional",
        "no rush",
        "when you get a chance"
    ]

    if any(
        signal in text_lower
        for signal in high_signals
    ):
        return "high"

    if any(
        signal in text_lower
        for signal in low_signals
    ):
        return "low"

    return "medium"


def extract_person(text):

    """
    Only extract a person when the message explicitly
    identifies someone with a simple 'with Name' pattern.

    Otherwise return None rather than guessing.
    """

    match = re.search(
        r"\bwith\s+"
        r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b",
        str(text)
    )

    if match:
        return match.group(1)

    return None


def extract_task_event(
    message,
    timestamp,
    message_id,
    sender,
    masked_message
):

    text_lower = str(message).lower()

    task_matches = [
        keyword
        for keyword in TASK_RULES
        if keyword in text_lower
    ]

    event_matches = [
        keyword
        for keyword in EVENT_RULES
        if keyword in text_lower
    ]

    if not task_matches and not event_matches:
        return None

    # Explicit event language takes precedence.
    if event_matches:

        item_type = "event"
        main_keyword = event_matches[0]
        title = main_keyword.title()

    else:

        item_type = "task"
        main_keyword = task_matches[0]
        title = main_keyword.title()

    date = extract_date(message)
    time = extract_time(message)
    person = extract_person(message)
    priority = determine_priority(message)

    # Never place an unmasked sensitive message
    # into the generated task/event output.
    description = masked_message

    return {
        "item_id": None,
        "type": item_type,
        "title": title,
        "description": description,
        "date_or_deadline": date,
        "time": time,
        "person": person,
        "priority": priority,
        "source_message_id": message_id
    }


# ============================================================
# 6. PROCESS ALL MESSAGES
# ============================================================

classification_results = []
task_event_results = []
sensitive_results = []


for _, row in df.iterrows():

    message_id = row["message_id"]
    timestamp = row["timestamp"]
    sender = row["sender"]
    message = str(row["message"])

    # -------------------------
    # Sensitive detection
    # -------------------------

    sensitive = detect_sensitive(message)

    # -------------------------
    # Classification
    # -------------------------

    classification = classify_message(
        message,
        sensitive
    )

    classification_results.append({

        "message_id": message_id,

        "category":
            classification["category"],

        "confidence":
            classification["confidence"],

        "reason":
            classification["reason"]
    })

    # -------------------------
    # Sensitive output
    # -------------------------

    if sensitive["is_sensitive"]:

        sensitive_results.append({

            "message_id":
                message_id,

            "sensitivity_type":
                sensitive["sensitivity_type"],

            "risk":
                sensitive["risk"],

            "masked_text":
                sensitive["masked_text"],

            "recommended_action":
                sensitive["recommended_action"]
        })

    # -------------------------
    # Task / event extraction
    # -------------------------

    task_event = extract_task_event(
        message,
        timestamp,
        message_id,
        sender,
        sensitive["masked_text"]
    )

    if task_event:

        task_event["item_id"] = (
            f"ITEM_{len(task_event_results) + 1:03d}"
        )

        task_event_results.append(task_event)


# ============================================================
# 7. CREATE DATAFRAMES
# ============================================================

classification_df = pd.DataFrame(
    classification_results
)

task_event_df = pd.DataFrame(
    task_event_results
)

sensitive_df = pd.DataFrame(
    sensitive_results
)


# ============================================================
# 8. MANDATORY 15 MESSAGE RESULTS
# ============================================================

mandatory_df = pd.read_csv(MANDATORY_PATH)

# Use the first column because the mandatory file
# may have a different column heading.
mandatory_ids = (
    mandatory_df.iloc[:, 0]
    .astype(str)
    .str.strip()
    .tolist()
)

mandatory_results = classification_df[
    classification_df["message_id"]
    .astype(str)
    .isin(mandatory_ids)
].copy()

# Preserve the order supplied by the mandatory file.
mandatory_results["order"] = (
    mandatory_results["message_id"]
    .astype(str)
    .apply(
        lambda x:
        mandatory_ids.index(x)
        if x in mandatory_ids
        else 999
    )
)

mandatory_results = (
    mandatory_results
    .sort_values("order")
    .drop(columns=["order"])
)


# ============================================================
# 9. SAVE CSV OUTPUTS
# ============================================================

classification_df.to_csv(
    OUTPUT_DIR / "classification_results.csv",
    index=False
)

task_event_df.to_csv(
    OUTPUT_DIR / "task_event_results.csv",
    index=False
)

sensitive_df.to_csv(
    OUTPUT_DIR / "sensitive_results.csv",
    index=False
)

mandatory_results.to_csv(
    OUTPUT_DIR / "mandatory_demo_results.csv",
    index=False
)


# ============================================================
# 10. SAVE JSON OUTPUTS
# ============================================================

with open(
    OUTPUT_DIR / "classification_results.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        classification_results,
        file,
        indent=2,
        ensure_ascii=False
    )


with open(
    OUTPUT_DIR / "task_event_results.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        task_event_results,
        file,
        indent=2,
        ensure_ascii=False
    )


with open(
    OUTPUT_DIR / "sensitive_results.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        sensitive_results,
        file,
        indent=2,
        ensure_ascii=False
    )


# ============================================================
# 11. SUMMARY
# ============================================================

print()
print("=" * 60)
print("MESSAGE INTELLIGENCE PIPELINE COMPLETE")
print("=" * 60)

print(f"Total messages processed: {len(df)}")

print()
print("Classification distribution:")
print(
    classification_df["category"]
    .value_counts()
    .to_string()
)

print()
print(
    f"Tasks/events extracted: "
    f"{len(task_event_results)}"
)

print(
    f"Sensitive messages detected: "
    f"{len(sensitive_results)}"
)

print(
    f"Mandatory IDs matched: "
    f"{len(mandatory_results)} / {len(mandatory_ids)}"
)

print()
print(f"Outputs saved to: {OUTPUT_DIR}")
print("=" * 60)