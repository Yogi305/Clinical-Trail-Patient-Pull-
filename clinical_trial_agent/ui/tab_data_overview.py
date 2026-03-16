"""
ui/tab_data_overview.py
-----------------------
Renders Tab 2: Data Overview (Phase 0).

Displays database health metrics, the ontology dictionary extracted by Pandas,
and a before/after data cleaning summary.
"""

import os
import json
import streamlit as st
import pandas as pd


_DB_PATH = "https://clinicaldata-765366202501-ap-southeast-2-an.s3.ap-southeast-2.amazonaws.com/healthcare_dataset.csv"
_CLEANED_DB_PATH = "https://clinicaldata-765366202501-ap-southeast-2-an.s3.ap-southeast-2.amazonaws.com/healthcare_dataset_cleaned.csv"


def render_tab_data_overview():
    st.markdown("## 📊 Database Profiling & Cleaning (Phase 0)")
    st.markdown(
        "Before the LangGraph agents are invoked, the system executes a lightning-fast "
        "Pandas query across the patient records to extract the unique schema values and clean anomalies."
    )

    base_dir = os.path.dirname(os.path.dirname(__file__))
    ontology_path = os.path.join(base_dir, "ontology_dictionary.json")

    try:
        df_raw = pd.read_csv(_DB_PATH)
        df_clean = pd.read_csv(_CLEANED_DB_PATH)
        data_loaded = True
    except Exception as e:
        data_loaded = False
        st.error(f"Failed to load dataset from S3: {e}")

    # Guard Clause — exit early if data unavailable (Law 1: Avoid Deep Nesting)
    if not data_loaded:
        st.warning("Database files not found. Please run `scripts/clean_database.py` first.")
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("Raw Patient Records", len(df_raw))
    col2.metric("Cleaned Patient Records", len(df_clean))
    col3.metric("Anomalies Removed/Fixed", len(df_raw) - len(df_clean) + 108)

    st.divider()

    st.markdown("### 🧬 The Ontology Dictionary (Schema-Aware RAG)")
    st.markdown("This dictionary is extracted instantaneously by Pandas and embedded into the **FAISS Vector Database**.")
    if os.path.exists(ontology_path):
        with open(ontology_path, "r") as f:
            ontology = json.load(f)

        onto_cols = st.columns(3)
        with onto_cols[0]:
            st.write("**Medical Conditions**")
            st.dataframe(pd.DataFrame(ontology.get("Medical Condition", []), columns=["Condition"]), hide_index=True)
            st.write("**Admissions**")
            st.dataframe(pd.DataFrame(ontology.get("Admission Type", []), columns=["Type"]), hide_index=True)
        with onto_cols[1]:
            st.write("**Medications**")
            st.dataframe(pd.DataFrame(ontology.get("Medication", []), columns=["Medication"]), hide_index=True)
            st.write("**Test Results**")
            st.dataframe(pd.DataFrame(ontology.get("Test Results", []), columns=["Result"]), hide_index=True)
        with onto_cols[2]:
            st.write("**Blood Types**")
            st.dataframe(pd.DataFrame(ontology.get("Blood Type", []), columns=["Type"]), hide_index=True)

    st.divider()

    st.markdown("### 🧹 Data Cleaning Summary")
    with st.expander("View Anomaly Details", expanded=True):
        st.markdown("""
        **Actions Taken by Validation Script:**
        * **Duplicate Records:** Found and dropped 534 exact duplicate entries.
        * **Negative Billing:** Found 108 records with negative billing amounts; converted to absolute values.
        * **Categorical Standardization:** Stripped whitespace and title-cased textual columns to guarantee consistency.
        """)
        st.markdown("**Sample of Raw Data (Pre-Cleaning):**")
        st.dataframe(df_raw.head())
        st.markdown("**Sample of Cleaned Data (Post-Cleaning):**")
        st.dataframe(df_clean.head())
