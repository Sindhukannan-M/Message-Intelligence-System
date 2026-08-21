import sys
import json
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PROJECT PATH
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="L2 Intelligence System",
    page_icon="🚀",
    layout="wide",
)


# ============================================================
# PATHS
# ============================================================

OUTPUT_DIR = ROOT / "outputs"
L2_OUTPUT_DIR = ROOT / "l2_outputs"


# ============================================================
# HELPERS
# ============================================================

def load_json(filename, default=None):

    path = L2_OUTPUT_DIR / filename

    if not path.exists():
        return default

    try:
        with open(
            path,
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    except Exception:
        return default


def json_to_dataframe(data):

    if data is None:
        return pd.DataFrame()

    if isinstance(data, list):
        return pd.DataFrame(data)

    if isinstance(data, dict):
        return pd.DataFrame([data])

    return pd.DataFrame()


# ============================================================
# TITLE
# ============================================================

st.title("🚀 L2 Intelligence System")

st.write(
    "An extension of the L1 Message Intelligence System "
    "for priority analysis, related-message grouping, "
    "semantic retrieval, privacy-aware routing, and benchmarking."
)


# ============================================================
# LOAD EXISTING L1 OUTPUTS
# ============================================================

classification_file = (
    OUTPUT_DIR / "classification_results.csv"
)

task_file = (
    OUTPUT_DIR / "task_event_results.csv"
)

sensitive_file = (
    OUTPUT_DIR / "sensitive_results.csv"
)

mandatory_file = (
    OUTPUT_DIR / "mandatory_demo_results.csv"
)


# ============================================================
# L1 SECTION
# ============================================================

st.header("L1 System")

try:

    classification_df = pd.read_csv(
        classification_file
    )

    task_df = pd.read_csv(
        task_file
    )

    sensitive_df = pd.read_csv(
        sensitive_file
    )

    mandatory_df = pd.read_csv(
        mandatory_file
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Messages",
            len(classification_df),
        )

    with col2:
        st.metric(
            "Tasks / Events",
            len(task_df),
        )

    with col3:
        st.metric(
            "Sensitive Messages",
            len(sensitive_df),
        )

    with col4:
        st.metric(
            "Mandatory Messages",
            len(mandatory_df),
        )

except FileNotFoundError:

    st.info(
        "L1 source datasets are intentionally kept "
        "outside the public repository."
    )


# ============================================================
# L2 OUTPUTS
# ============================================================

st.divider()

st.header("🚀 L2 Processing Results")


priority_data = load_json(
    "priority_results.json",
    [],
)

related_data = load_json(
    "related_groups.json",
    [],
)

privacy_data = load_json(
    "privacy_routing_results.json",
    [],
)

benchmark_data = load_json(
    "benchmark_comparison.json",
    {},
)


priority_df = json_to_dataframe(
    priority_data
)

related_df = json_to_dataframe(
    related_data
)

privacy_df = json_to_dataframe(
    privacy_data
)


# ============================================================
# L2 STATUS
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Priority Results",
        len(priority_df),
    )

with col2:

    st.metric(
        "Related Groups",
        len(related_df),
    )

with col3:

    st.metric(
        "Privacy Decisions",
        len(privacy_df),
    )


# ============================================================
# L2 RESULTS BUTTON
# ============================================================

st.subheader("L2 Pipeline")

if st.button(
    "Run L2 Pipeline Results"
):

    if (
        priority_df.empty
        and related_df.empty
        and privacy_df.empty
    ):

        st.error(
            "L2 result files are not available."
        )

    else:

        st.success(
            "L2 structured results loaded successfully."
        )

        st.session_state[
            "l2_loaded"
        ] = True


if st.session_state.get(
    "l2_loaded",
    False,
):

    st.success(
        "L2 results are ready for demonstration."
    )


# ============================================================
# PRIORITY
# ============================================================

st.divider()

st.header("🎯 Priority and Action Engine")

if priority_df.empty:

    st.warning(
        "Priority results are unavailable."
    )

else:

    if "priority" in priority_df.columns:

        st.subheader(
            "Priority Distribution"
        )

        st.bar_chart(
            priority_df[
                "priority"
            ].value_counts()
        )

    display_columns = [
        "message_id",
        "item_id",
        "priority",
        "priority_reason",
        "priority_signals",
        "priority_confidence",
        "priority_updated",
    ]

    available = [
        column
        for column in display_columns
        if column in priority_df.columns
    ]

    st.dataframe(
        priority_df[available],
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# RELATED MESSAGE GROUPING
# ============================================================

st.divider()

st.header("🔗 Related-Message Groups")

if related_df.empty:

    st.warning(
        "Related-message results are unavailable."
    )

else:

    st.write(
        "Messages referring to the same task, event, "
        "request, or subject are represented as groups."
    )

    st.dataframe(
        related_df,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# SEMANTIC SEARCH
# ============================================================

st.divider()

st.header("🔎 L2 Semantic Search")

st.write(
    "Search the generated L2 evidence without exposing "
    "the original supplied datasets."
)

query = st.text_input(
    "Ask a question about the messages",
    placeholder=(
        "What tasks should I complete today?"
    ),
)


def search_results(query_text):

    query_text = query_text.lower()

    results = []

    # Search priority results.
    for _, row in priority_df.iterrows():

        text = " ".join(
            str(value)
            for value in row.tolist()
        ).lower()

        score = sum(
            word in text
            for word in query_text.split()
            if len(word) > 2
        )

        if score > 0:

            results.append(
                {
                    "message_id": row.get(
                        "message_id",
                        row.get(
                            "source_message_id",
                            "",
                        ),
                    ),
                    "item_id": row.get(
                        "item_id",
                        "",
                    ),
                    "evidence": row.get(
                        "priority_reason",
                        "",
                    ),
                    "relevance_score": score,
                }
            )

    results.sort(
        key=lambda x: x[
            "relevance_score"
        ],
        reverse=True,
    )

    return pd.DataFrame(
        results[:5]
    )


if query:

    results_df = search_results(
        query
    )

    if results_df.empty:

        st.warning(
            "Insufficient evidence to answer this question."
        )

    else:

        st.subheader(
            "Retrieved Evidence"
        )

        st.dataframe(
            results_df,
            use_container_width=True,
            hide_index=True,
        )

        st.info(
            "Answer supported by the retrieved "
            "structured evidence shown above."
        )


# ============================================================
# PRIVACY ROUTING
# ============================================================

st.divider()

st.header("🔐 Privacy-Aware Routing")

privacy_request = st.text_input(
    "Enter a request to check its privacy route",
    placeholder=(
        "Example: Analyze this personal information"
    ),
)


if privacy_request:

    try:

        from src.privacy_router import (
            route_request,
        )

        request_lower = (
            privacy_request.lower()
        )

        sensitive_keywords = [
            "password",
            "token",
            "credit card",
            "bank account",
            "social security",
            "authentication",
        ]

        high_risk_keywords = [
            "password",
            "token",
            "authentication",
        ]

        contains_sensitive = any(
            keyword in request_lower
            for keyword in sensitive_keywords
        )

        high_risk = any(
            keyword in request_lower
            for keyword in high_risk_keywords
        )

        result = route_request(
            contains_sensitive_data=(
                contains_sensitive
            ),
            sensitivity_type=(
                "sensitive_information"
                if contains_sensitive
                else None
            ),
            external_service_requested=False,
            high_risk=high_risk,
        )

        st.write(
            f"**Route:** `{result['route']}`"
        )

        st.write(
            f"**Reason:** {result['reason']}"
        )

        if result.get("signals"):

            st.write(
                "**Signals:** "
                + ", ".join(
                    result["signals"]
                )
            )

    except Exception as error:

        st.error(
            f"Privacy routing error: {error}"
        )


# ============================================================
# BENCHMARK
# ============================================================

st.divider()

st.header("📊 Benchmark Comparison")

if not benchmark_data:

    st.warning(
        "Benchmark results are unavailable."
    )

else:

    st.json(
        benchmark_data
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Message Intelligence System | "
    "L1 + L2 explainable processing pipeline"
)