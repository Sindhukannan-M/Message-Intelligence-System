import sys
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


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

ROOT = PROJECT_ROOT
OUTPUT_DIR = ROOT / "outputs"

L1_DATASET = ROOT / "data" / "l1" / "messages.csv"
L2_DATASET = ROOT / "data" / "l2" / "l2_messages.csv"
L2_DEMO_DATASET = (
    ROOT / "data" / "l2" / "l2_demo_messages.csv"
)


# ============================================================
# TITLE
# ============================================================

st.title("💬 Message Intelligence System")

st.write(
    "L1 + L2 message processing system for "
    "classification, task extraction, priority analysis, "
    "related-message grouping, semantic retrieval, "
    "and privacy-aware routing."
)


# ============================================================
# L1 OUTPUTS
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
# LOAD EXISTING L1 OUTPUTS
# ============================================================

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
        "Required L1 output files are not available."
    )

    st.info(
        "The full L1/L2 processing pipeline runs locally "
        "with the supplied datasets. The hosted application "
        "requires the generated L1 outputs to be present."
    )

    st.stop()


# ============================================================
# DASHBOARD METRICS
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "L1 Messages",
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


st.divider()


# ============================================================
# L1 NAVIGATION
# ============================================================

section = st.selectbox(
    "Choose a section",
    [
        "Classification",
        "Tasks & Events",
        "Sensitive Information",
        "Mandatory Demo",
    ],
)


# ============================================================
# CLASSIFICATION
# ============================================================

if section == "Classification":

    st.header("Message Classification")

    if "category" in classification_df.columns:

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


# ============================================================
# TASKS AND EVENTS
# ============================================================

elif section == "Tasks & Events":

    st.header("Tasks and Events")

    if task_df.empty:

        st.info(
            "No tasks or events were extracted."
        )

    else:

        if "priority" in task_df.columns:

            st.subheader(
                "Priority Distribution"
            )

            st.bar_chart(
                task_df["priority"].value_counts()
            )

        st.subheader(
            "Extracted Tasks and Events"
        )

        st.dataframe(
            task_df,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# SENSITIVE INFORMATION
# ============================================================

elif section == "Sensitive Information":

    st.header(
        "Sensitive Information"
    )

    st.warning(
        "Sensitive values are masked in the output."
    )

    if sensitive_df.empty:

        st.success(
            "No sensitive information detected."
        )

    else:

        st.dataframe(
            sensitive_df,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# MANDATORY DEMO
# ============================================================

elif section == "Mandatory Demo":

    st.header(
        "Mandatory 15 Message Demonstration"
    )

    st.write(
        "Mandatory demonstration results generated "
        "by the processing pipeline."
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

st.header(
    "🚀 L2 Intelligence System"
)


# ------------------------------------------------------------
# Check whether private datasets are available
# ------------------------------------------------------------

datasets_available = (
    L1_DATASET.exists()
    and L2_DATASET.exists()
)

demo_dataset_available = (
    L2_DEMO_DATASET.exists()
)


# ============================================================
# L2 PIPELINE
# ============================================================

if datasets_available:

    try:

        from src.l2_pipeline import (
            run_l2_pipeline,
        )

        if (
            "l2_pipeline"
            not in st.session_state
        ):

            st.session_state.l2_pipeline = None

        if st.button(
            "Run L2 Pipeline"
        ):

            with st.spinner(
                "Processing L1 + L2 messages..."
            ):

                st.session_state.l2_pipeline = (
                    run_l2_pipeline()
                )

        if (
            st.session_state.l2_pipeline
            is not None
        ):

            pipeline = (
                st.session_state.l2_pipeline
            )

            messages = pipeline[
                "messages"
            ]

            related_groups = pipeline[
                "related_groups"
            ]

            st.success(
                "L2 pipeline processed successfully."
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "L1 Messages",
                    len(
                        messages[
                            messages["source"]
                            == "L1"
                        ]
                    ),
                )

            with col2:

                st.metric(
                    "L2 Messages",
                    len(
                        messages[
                            messages["source"]
                            == "L2"
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

    except Exception as error:

        st.error(
            "The L2 pipeline could not be initialized."
        )

        st.caption(
            f"Pipeline error: {error}"
        )

else:

    st.info(
        "The full L2 dataset is available only in "
        "the local development environment. "
        "The supplied L1/L2 datasets are intentionally "
        "not included in the public repository."
    )


# ============================================================
# L2 SEMANTIC SEARCH
# ============================================================

st.divider()

st.header(
    "🔎 L2 Semantic Search"
)

search_query = st.text_input(
    "Ask a question about the messages",
    placeholder=(
        "What tasks should I complete today?"
    ),
)


if search_query:

    pipeline = (
        st.session_state.get(
            "l2_pipeline"
        )
    )

    if pipeline is None:

        st.warning(
            "Run the L2 Pipeline first in the "
            "local environment to search the "
            "full message collection."
        )

    else:

        search_engine = pipeline[
            "search_engine"
        ]

        with st.spinner(
            "Searching messages..."
        ):

            search_results = (
                search_engine.search(
                    search_query,
                    top_k=5,
                )
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
                "Insufficient evidence to answer "
                "this question."
            )


# ============================================================
# PRIVACY-AWARE ROUTING
# ============================================================

st.divider()

st.header(
    "🔐 Privacy-Aware Routing"
)

try:

    from src.privacy_router import (
        route_request,
    )

    privacy_request = st.text_input(
        "Enter a request to check its privacy route",
        placeholder=(
            "Example: Analyze this personal information"
        ),
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

        high_risk_keywords = [
            "password",
            "token",
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
            for keyword in high_risk_keywords
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
            f"**Route:** "
            f"`{route_result['route']}`"
        )

        st.write(
            f"**Reason:** "
            f"{route_result['reason']}"
        )

        if route_result.get(
            "signals"
        ):

            st.write(
                "**Signals:** "
                + ", ".join(
                    route_result["signals"]
                )
            )

except ImportError as error:

    st.error(
        f"Privacy router unavailable: {error}"
    )


# ============================================================
# L2 UNSEEN DEMO BATCH
# ============================================================

st.divider()

st.header(
    "🧪 L2 Unseen Demo Batch"
)

if demo_dataset_available:

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

                demo_df = (
                    load_demo_messages()
                )

            st.success(
                f"Loaded {len(demo_df)} "
                "unseen demo messages."
            )

            display_columns = [
                "message_id",
                "timestamp",
                "sender",
                "message",
            ]

            available_columns = [
                column
                for column in display_columns
                if column in demo_df.columns
            ]

            st.dataframe(
                demo_df[
                    available_columns
                ],
                use_container_width=True,
                hide_index=True,
            )

    except Exception as error:

        st.error(
            f"Demo batch could not be loaded: {error}"
        )

else:

    st.info(
        "The unseen L2 demonstration dataset is "
        "kept outside the public repository."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Message Intelligence System | "
    "Rule-based L1 + L2 explainable processing pipeline"
)