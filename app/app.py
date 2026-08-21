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
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Message Intelligence System",
    page_icon="💬",
    layout="wide",
)


# ============================================================
# PATHS
# ============================================================

OUTPUT_DIR = ROOT / "outputs"
L2_OUTPUT_DIR = ROOT / "l2_outputs"

L1_DATASET = ROOT / "data" / "l1" / "messages.csv"
L2_DATASET = ROOT / "data" / "l2" / "l2_messages.csv"
L2_DEMO_DATASET = ROOT / "data" / "l2" / "l2_demo_messages.csv"


# ============================================================
# HELPERS
# ============================================================

def load_json(filename, default=None):
    path = L2_OUTPUT_DIR / filename

    if not path.exists():
        return default

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return default


def as_dataframe(data):
    if data is None:
        return pd.DataFrame()

    if isinstance(data, list):
        return pd.DataFrame(data)

    if isinstance(data, dict):
        return pd.DataFrame([data])

    return pd.DataFrame()


def get_value(row, *keys):
    for key in keys:
        if key in row and pd.notna(row[key]):
            return row[key]
    return ""


# ============================================================
# TITLE
# ============================================================

st.title("💬 Message Intelligence System")

st.write(
    "An explainable L1 + L2 message intelligence system "
    "for classification, task and event analysis, "
    "priority reasoning, related-message grouping, "
    "semantic retrieval, and privacy-aware routing."
)


# ============================================================
# L1 OUTPUTS
# ============================================================

classification_file = OUTPUT_DIR / "classification_results.csv"
task_file = OUTPUT_DIR / "task_event_results.csv"
sensitive_file = OUTPUT_DIR / "sensitive_results.csv"
mandatory_file = OUTPUT_DIR / "mandatory_demo_results.csv"


try:
    classification_df = pd.read_csv(classification_file)
    task_df = pd.read_csv(task_file)
    sensitive_df = pd.read_csv(sensitive_file)
    mandatory_df = pd.read_csv(mandatory_file)

    l1_outputs_available = True

except FileNotFoundError:
    classification_df = pd.DataFrame()
    task_df = pd.DataFrame()
    sensitive_df = pd.DataFrame()
    mandatory_df = pd.DataFrame()

    l1_outputs_available = False


# ============================================================
# L1 DASHBOARD
# ============================================================

st.header("L1 System")

if l1_outputs_available:

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Messages", len(classification_df))

    with col2:
        st.metric("Tasks / Events", len(task_df))

    with col3:
        st.metric("Sensitive Messages", len(sensitive_df))

    with col4:
        st.metric("Mandatory Messages", len(mandatory_df))

    with st.expander("Classification Results"):

        if "category" in classification_df.columns:

            st.subheader("Category Distribution")

            st.bar_chart(
                classification_df["category"].value_counts()
            )

        st.dataframe(
            classification_df,
            use_container_width=True,
            hide_index=True,
        )

    with st.expander("L1 Tasks and Events"):

        st.dataframe(
            task_df,
            use_container_width=True,
            hide_index=True,
        )

    with st.expander("L1 Sensitive Information"):

        st.warning(
            "Sensitive values are masked in the generated output."
        )

        st.dataframe(
            sensitive_df,
            use_container_width=True,
            hide_index=True,
        )

    with st.expander("Mandatory L1 Demonstration"):

        st.dataframe(
            mandatory_df,
            use_container_width=True,
            hide_index=True,
        )

else:

    st.info(
        "The original L1/L2 datasets are intentionally kept "
        "outside the public repository. Generated structured "
        "results are used for the hosted demonstration."
    )


# ============================================================
# L2 RESULTS
# ============================================================

st.divider()

st.header("🚀 L2 Extension")


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


priority_df = as_dataframe(priority_data)
related_df = as_dataframe(related_data)
privacy_df = as_dataframe(privacy_data)


# ============================================================
# L2 OVERVIEW
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
        "Privacy Results",
        len(privacy_df),
    )


# ============================================================
# LOCAL FULL PIPELINE
# ============================================================

local_pipeline_available = (
    L1_DATASET.exists()
    and L2_DATASET.exists()
)

if local_pipeline_available:

    st.subheader("Full L2 Pipeline")

    if "full_l2_pipeline" not in st.session_state:
        st.session_state.full_l2_pipeline = None

    if st.button("Run Full L2 Pipeline"):

        try:

            from src.l2_pipeline import run_l2_pipeline

            with st.spinner(
                "Processing L1 + L2 messages..."
            ):

                st.session_state.full_l2_pipeline = (
                    run_l2_pipeline()
                )

            st.success(
                "Full L2 pipeline processed successfully."
            )

        except Exception as error:

            st.error(
                f"L2 pipeline error: {error}"
            )

    pipeline = st.session_state.full_l2_pipeline

else:

    pipeline = None

    st.info(
        "Hosted mode: the supplied datasets are not included "
        "in the public repository. The generated L2 results "
        "below are used for the cloud demonstration."
    )


# ============================================================
# PRIORITY ENGINE
# ============================================================

st.divider()

st.header("🎯 Priority and Action Engine")

st.write(
    "Priority represents how urgently an actionable item "
    "requires attention. The engine combines deadline "
    "proximity, urgency, action signals, response requirements, "
    "sensitivity, and status."
)

if priority_df.empty:

    st.warning(
        "Priority results are not available."
    )

else:

    if "priority" in priority_df.columns:

        st.subheader("Priority Distribution")

        st.bar_chart(
            priority_df["priority"].value_counts()
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

    available_columns = [
        column
        for column in display_columns
        if column in priority_df.columns
    ]

    if available_columns:

        st.subheader("Priority Decisions")

        st.dataframe(
            priority_df[available_columns],
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.dataframe(
            priority_df,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# RELATED MESSAGE GROUPING
# ============================================================

st.divider()

st.header("🔗 Related-Message Groups")

st.write(
    "Messages are grouped according to their relationship "
    "to the same task, event, request, or subject while "
    "preserving chronological context."
)

if related_df.empty:

    st.warning(
        "Related-message groups are not available."
    )

else:

    # Summary table
    summary_columns = [
        "group_id",
        "title",
        "status",
        "latest_deadline",
        "confidence",
    ]

    available_summary = [
        column
        for column in summary_columns
        if column in related_df.columns
    ]

    if available_summary:

        st.dataframe(
            related_df[available_summary],
            use_container_width=True,
            hide_index=True,
        )

    # Detailed expandable examples
    st.subheader("Group Details")

    for index, row in related_df.head(5).iterrows():

        group_id = get_value(
            row,
            "group_id",
        )

        title = get_value(
            row,
            "title",
            "group_title",
        )

        label = (
            f"{group_id} — {title}"
            if group_id or title
            else f"Group {index + 1}"
        )

        with st.expander(label):

            for field in [
                "group_id",
                "title",
                "related_message_ids",
                "related_task_event_ids",
                "status",
                "latest_deadline",
                "summary",
                "confidence",
            ]:

                if field in row:

                    st.write(
                        f"**{field}:** {row[field]}"
                    )


# ============================================================
# SEMANTIC SEARCH
# ============================================================

st.divider()

st.header("🔎 L2 Semantic Search")

st.write(
    "The local L2 implementation uses the project's "
    "SemanticSearch component for retrieval. When the "
    "full pipeline is unavailable in the hosted environment, "
    "the generated L2 evidence remains available for review."
)

search_query = st.text_input(
    "Ask a question about the messages",
    placeholder=(
        "What tasks should I complete today?"
    ),
)


def run_local_semantic_search(query):

    if pipeline is None:
        return pd.DataFrame()

    search_engine = pipeline.get(
        "search_engine"
    )

    if search_engine is None:
        return pd.DataFrame()

    results = search_engine.search(
        query,
        top_k=5,
    )

    if not results:
        return pd.DataFrame()

    return pd.DataFrame(results)


def run_structured_evidence_search(query):

    if priority_df.empty:
        return pd.DataFrame()

    words = [
        word.lower()
        for word in query.split()
        if len(word) > 2
    ]

    matches = []

    for _, row in priority_df.iterrows():

        row_text = " ".join(
            str(value)
            for value in row.tolist()
        ).lower()

        score = sum(
            word in row_text
            for word in words
        )

        if score > 0:

            matches.append(
                {
                    "message_id": get_value(
                        row,
                        "message_id",
                        "source_message_id",
                    ),
                    "item_id": get_value(
                        row,
                        "item_id",
                    ),
                    "priority": get_value(
                        row,
                        "priority",
                    ),
                    "evidence": get_value(
                        row,
                        "priority_reason",
                        "reason",
                    ),
                    "relevance_score": score,
                }
            )

    matches.sort(
        key=lambda item: item[
            "relevance_score"
        ],
        reverse=True,
    )

    return pd.DataFrame(
        matches[:5]
    )


if search_query:

    with st.spinner("Retrieving evidence..."):

        if pipeline is not None:

            search_results = run_local_semantic_search(
                search_query
            )

            retrieval_mode = (
                "SemanticSearch"
            )

        else:

            search_results = (
                run_structured_evidence_search(
                    search_query
                )
            )

            retrieval_mode = (
                "Generated L2 evidence"
            )

    if search_results.empty:

        st.warning(
            "Insufficient evidence to answer this question."
        )

    else:

        st.subheader("Retrieved Evidence")

        st.caption(
            f"Retrieval source: {retrieval_mode}"
        )

        st.dataframe(
            search_results,
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Evidence Explanation")

        st.write(
            "The displayed records are the evidence retrieved "
            "for the query. The system does not invent an answer "
            "when sufficient evidence is unavailable."
        )


# ============================================================
# PRIVACY-AWARE ROUTING
# ============================================================

st.divider()

st.header("🔐 Privacy-Aware Routing")

st.write(
    "Requests are routed according to sensitivity, risk, "
    "and whether an external service is requested."
)

privacy_request = st.text_input(
    "Enter a privacy-sensitive request",
    placeholder=(
        "Example: Analyze this personal information"
    ),
)

external_requested = st.checkbox(
    "External service requested",
)

if privacy_request:

    try:

        from src.privacy_router import route_request

        request_lower = privacy_request.lower()

        sensitive_keywords = [
            "password",
            "token",
            "credit card",
            "bank account",
            "social security",
            "authentication",
            "otp",
            "pin",
            "cvv",
        ]

        high_risk_keywords = [
            "password",
            "token",
            "authentication",
            "otp",
            "pin",
            "cvv",
        ]

        contains_sensitive = any(
            keyword in request_lower
            for keyword in sensitive_keywords
        )

        high_risk = any(
            keyword in request_lower
            for keyword in high_risk_keywords
        )

        route_result = route_request(
            contains_sensitive_data=(
                contains_sensitive
            ),
            sensitivity_type=(
                "sensitive_information"
                if contains_sensitive
                else None
            ),
            external_service_requested=(
                external_requested
            ),
            high_risk=high_risk,
        )

        st.subheader("Routing Decision")

        st.write(
            f"**Route:** `{route_result['route']}`"
        )

        st.write(
            f"**Reason:** {route_result['reason']}"
        )

        signals = route_result.get(
            "signals",
            [],
        )

        if signals:

            st.write(
                "**Signals:** "
                + ", ".join(signals)
            )

    except Exception as error:

        st.error(
            f"Privacy routing error: {error}"
        )


# ============================================================
# MASKED SENSITIVE RESULTS
# ============================================================

if not sensitive_df.empty:

    st.subheader(
        "🛡️ Masked Sensitive Information"
    )

    st.warning(
        "Sensitive values are shown only in masked form."
    )

    st.dataframe(
        sensitive_df,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# BENCHMARK
# ============================================================

st.divider()

st.header("📊 Benchmark Comparison")

if not benchmark_data:

    st.warning(
        "Benchmark results are not available."
    )

else:

    original = benchmark_data.get(
        "original",
        {},
    )

    optimized = benchmark_data.get(
        "optimized",
        {},
    )

    improvement = benchmark_data.get(
        "improvement",
        {},
    )

    benchmark_table = pd.DataFrame(
        {
            "Metric": [
                "Response time (seconds)",
                "Size (KB)",
                "Result quality",
            ],
            "Original": [
                original.get(
                    "response_time_seconds"
                ),
                original.get(
                    "size_kb"
                ),
                original.get(
                    "quality"
                ),
            ],
            "Optimized": [
                optimized.get(
                    "response_time_seconds"
                ),
                optimized.get(
                    "size_kb"
                ),
                optimized.get(
                    "quality"
                ),
            ],
        }
    )

    st.dataframe(
        benchmark_table,
        use_container_width=True,
        hide_index=True,
    )

    speed_change = improvement.get(
        "response_time_change_percent"
    )

    if speed_change is not None:

        st.metric(
            "Response-time improvement",
            f"{speed_change}%",
        )

    st.caption(
        "Benchmark measurements were generated by the "
        "project benchmark module using the same workload "
        "for the compared versions."
    )


# ============================================================
# L2 UNSEEN DEMO
# ============================================================

st.divider()

st.header("🧪 L2 Unseen Demo Batch")

if L2_DEMO_DATASET.exists():

    try:

        from src.l2_demo import (
            load_demo_messages,
        )

        if st.button(
            "Load L2 Demo Messages"
        ):

            with st.spinner(
                "Loading unseen L2 demo batch..."
            ):

                demo_df = load_demo_messages()

            st.success(
                f"Loaded {len(demo_df)} unseen demo messages."
            )

            display_columns = [
                "message_id",
                "timestamp",
                "sender",
                "message",
            ]

            available = [
                column
                for column in display_columns
                if column in demo_df.columns
            ]

            st.dataframe(
                demo_df[available],
                use_container_width=True,
                hide_index=True,
            )

    except Exception as error:

        st.error(
            f"Unable to load demo messages: {error}"
        )

else:

    st.info(
        "The unseen L2 demonstration dataset is kept "
        "outside the public repository."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Message Intelligence System | "
    "Rule-based and explainable L1 + L2 processing pipeline"
)