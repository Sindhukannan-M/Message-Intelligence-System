import sys
from pathlib import Path

import pandas as pd
import streamlit as st


# ------------------------------------------------------------
# Project path
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ------------------------------------------------------------
# Page configuration
# ------------------------------------------------------------

st.set_page_config(
    page_title="Message Intelligence System",
    page_icon="💬",
    layout="wide",
)


# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------

ROOT = PROJECT_ROOT
OUTPUT_DIR = ROOT / "outputs"


# ------------------------------------------------------------
# Title
# ------------------------------------------------------------

st.title("💬 Message Intelligence System")

st.write(
    "Classify messages, identify tasks and events, "
    "detect sensitive information, and process L2 intelligence."
)


# ------------------------------------------------------------
# Load L1 outputs
# ------------------------------------------------------------

classification_file = OUTPUT_DIR / "classification_results.csv"
task_file = OUTPUT_DIR / "task_event_results.csv"
sensitive_file = OUTPUT_DIR / "sensitive_results.csv"
mandatory_file = OUTPUT_DIR / "mandatory_demo_results.csv"


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

except FileNotFoundError:

    st.error(
        "Output files were not found. "
        "Run src/main.py first."
    )

    st.stop()


# ------------------------------------------------------------
# Dashboard metrics
# ------------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Messages",
        len(classification_df)
    )

with col2:
    st.metric(
        "Tasks / Events",
        len(task_df)
    )

with col3:
    st.metric(
        "Sensitive Messages",
        len(sensitive_df)
    )

with col4:
    st.metric(
        "Mandatory Messages",
        len(mandatory_df)
    )


st.divider()


# ------------------------------------------------------------
# L1 Navigation
# ------------------------------------------------------------

section = st.selectbox(
    "Choose a section",
    [
        "Classification",
        "Tasks & Events",
        "Sensitive Information",
        "Mandatory Demo",
    ],
)


# ------------------------------------------------------------
# Classification
# ------------------------------------------------------------

if section == "Classification":

    st.header("Message Classification")

    category_counts = (
        classification_df["category"]
        .value_counts()
    )

    st.subheader("Category Distribution")

    st.bar_chart(category_counts)

    st.subheader("Classification Results")

    st.dataframe(
        classification_df,
        use_container_width=True,
        hide_index=True,
    )


# ------------------------------------------------------------
# Tasks and Events
# ------------------------------------------------------------

elif section == "Tasks & Events":

    st.header("Tasks and Events")

    if task_df.empty:

        st.info(
            "No tasks or events were extracted."
        )

    else:

        if "priority" in task_df.columns:

            st.subheader("Priority Distribution")

            priority_counts = (
                task_df["priority"]
                .value_counts()
            )

            st.bar_chart(priority_counts)

        st.subheader(
            "Extracted Tasks and Events"
        )

        st.dataframe(
            task_df,
            use_container_width=True,
            hide_index=True,
        )


# ------------------------------------------------------------
# Sensitive Information
# ------------------------------------------------------------

elif section == "Sensitive Information":

    st.header("Sensitive Information")

    st.warning(
        "Sensitive values are masked in the output."
    )

    if sensitive_df.empty:

        st.success(
            "No sensitive information detected."
        )

    else:

        st.subheader(
            "Sensitive Information Results"
        )

        st.dataframe(
            sensitive_df,
            use_container_width=True,
            hide_index=True,
        )


# ------------------------------------------------------------
# Mandatory Demo
# ------------------------------------------------------------

elif section == "Mandatory Demo":

    st.header(
        "Mandatory 15 Message Demonstration"
    )

    st.write(
        "These are the messages required for "
        "the demonstration."
    )

    st.dataframe(
        mandatory_df,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# L2 SYSTEM
# ============================================================

st.divider()

st.header("🚀 L2 Intelligence System")


# ------------------------------------------------------------
# Import L2 components
# ------------------------------------------------------------

from src.l2_pipeline import run_l2_pipeline
from src.privacy_router import route_request
from src.l2_demo import load_demo_messages


# ------------------------------------------------------------
# Initialize L2 pipeline
# ------------------------------------------------------------

@st.cache_resource
def get_l2_pipeline():

    return run_l2_pipeline()


# ------------------------------------------------------------
# Run L2 Pipeline
# ------------------------------------------------------------

if st.button("Run L2 Pipeline"):

    with st.spinner(
        "Processing L1 + L2 messages..."
    ):

        pipeline = get_l2_pipeline()

    messages = pipeline["messages"]
    related_groups = pipeline["related_groups"]

    st.success(
        "L2 pipeline processed successfully."
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "L1 Messages",
            len(
                messages[
                    messages["source"] == "L1"
                ]
            ),
        )

    with col2:

        st.metric(
            "L2 Messages",
            len(
                messages[
                    messages["source"] == "L2"
                ]
            ),
        )

    with col3:

        st.metric(
            "Related Groups",
            len(related_groups),
        )

    st.subheader(
        "Related Message Groups"
    )

    st.dataframe(
        related_groups,
        use_container_width=True,
        hide_index=True,
    )


# ------------------------------------------------------------
# L2 Semantic Search
# ------------------------------------------------------------

st.divider()

st.header("🔎 L2 Semantic Search")

search_query = st.text_input(
    "Ask a question about the messages",
    placeholder="What tasks should I complete today?",
)

if search_query:

    with st.spinner(
        "Searching messages..."
    ):

        pipeline = get_l2_pipeline()

        search_engine = (
            pipeline["search_engine"]
        )

        search_results = search_engine.search(
            search_query,
            top_k=5,
        )

    if search_results:

        st.subheader(
            "Retrieved Evidence"
        )

        st.dataframe(
            search_results,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.warning(
            "Insufficient evidence to answer this question."
        )


# ------------------------------------------------------------
# L2 Privacy-Aware Routing
# ------------------------------------------------------------

st.divider()

st.header("🔐 Privacy-Aware Routing")

privacy_request = st.text_input(
    "Enter a request to check its privacy route",
    placeholder="Example: Analyze this personal information",
)

if privacy_request:

    sensitive_keywords = [
        "password",
        "token",
        "credit card",
        "bank account",
        "social security",
        "authentication",
    ]

    request_lower = (
        privacy_request.lower()
    )

    detected_sensitive = any(
        keyword in request_lower
        for keyword in sensitive_keywords
    )

    high_risk = any(
        keyword in request_lower
        for keyword in [
            "password",
            "token",
            "authentication",
        ]
    )

    route_result = route_request(
        contains_sensitive_data=(
            detected_sensitive
        ),
        sensitivity_type=(
            "sensitive_information"
            if detected_sensitive
            else None
        ),
        external_service_requested=False,
        high_risk=high_risk,
    )

    st.write(
        f"**Route:** `{route_result['route']}`"
    )

    st.write(
        f"**Reason:** {route_result['reason']}"
    )

    if route_result["signals"]:

        st.write(
            "**Signals:** "
            + ", ".join(
                route_result["signals"]
            )
        )


# ------------------------------------------------------------
# L2 Unseen Demo Batch
# ------------------------------------------------------------

st.divider()

st.header(
    "🧪 L2 Unseen Demo Batch"
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

    st.dataframe(
        demo_df[
            [
                "message_id",
                "timestamp",
                "sender",
                "message",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


# ------------------------------------------------------------
# L2 Demo Queries
# ------------------------------------------------------------

st.divider()

st.header(
    "💬 L2 Demo Queries"
)

demo_queries_file = (
    ROOT
    / "data"
    / "l2"
    / "l2_demo_queries.csv"
)

if demo_queries_file.exists():

    demo_queries_df = pd.read_csv(
        demo_queries_file
    )

    st.write(
        f"Loaded {len(demo_queries_df)} demo queries."
    )

    query_columns = [
        column
        for column in demo_queries_df.columns
        if "query" in column.lower()
    ]

    if query_columns:

        query_column = query_columns[0]

        selected_query = st.selectbox(
            "Select a supplied demo query",
            demo_queries_df[
                query_column
            ].tolist(),
        )

        if st.button(
            "Run Selected Query"
        ):

            pipeline = get_l2_pipeline()

            search_engine = (
                pipeline["search_engine"]
            )

            results = search_engine.search(
                selected_query,
                top_k=5,
            )

            st.subheader(
                "Retrieved Evidence"
            )

            if results:

                st.dataframe(
                    results,
                    use_container_width=True,
                    hide_index=True,
                )

            else:

                st.warning(
                    "Insufficient evidence "
                    "to answer this query."
                )

    else:

        st.warning(
            "No query column was found "
            "in the supplied demo file."
        )

else:

    st.warning(
        "L2 demo queries file was not found."
    )


# ------------------------------------------------------------
# Footer
# ------------------------------------------------------------

st.divider()

st.caption(
    "Message Intelligence System | "
    "L1 + L2 explainable processing pipeline"
)