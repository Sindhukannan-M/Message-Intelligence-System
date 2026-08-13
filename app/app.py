import streamlit as st
import pandas as pd
from pathlib import Path


# ------------------------------------------------------------
# Page configuration
# ------------------------------------------------------------

st.set_page_config(
    page_title="Message Intelligence System",
    page_icon="💬",
    layout="wide"
)


# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "outputs"


# ------------------------------------------------------------
# Title
# ------------------------------------------------------------

st.title("💬 Message Intelligence System")

st.write(
    "Classify messages, identify tasks and events, "
    "and detect sensitive information."
)


# ------------------------------------------------------------
# Load outputs
# ------------------------------------------------------------

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
# Navigation
# ------------------------------------------------------------

section = st.selectbox(
    "Choose a section",
    [
        "Classification",
        "Tasks & Events",
        "Sensitive Information",
        "Mandatory Demo"
    ]
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
        hide_index=True
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
            hide_index=True
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
            hide_index=True
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
        hide_index=True
    )


# ------------------------------------------------------------
# Footer
# ------------------------------------------------------------

st.divider()

st.caption(
    "Message Intelligence System | "
    "Rule-based explainable processing pipeline"
)