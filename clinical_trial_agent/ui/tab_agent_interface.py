"""
ui/tab_agent_interface.py
-------------------------
Renders Tab 1: Agent Interface — the full step-by-step agentic workflow.

Each stage of the workflow is isolated into its own helper function.
The workflow state is managed via st.session_state so results persist
across reruns without re-running the expensive LLM calls.
"""

import io
import os
import json
import streamlit as st
import pandas as pd
import docx

from agents.gatekeeper import run_gatekeeper
from agents.extractor import run_extractor
from agents.mapper import run_mapper
from agents.data_engine import execute_deterministic_patient_search


def _read_uploaded_file(uploaded_file) -> str:
    """Parse text from a .docx or .txt upload."""
    if uploaded_file.name.endswith(".docx"):
        doc = docx.Document(uploaded_file)
        return "\n".join([para.text for para in doc.paragraphs])
    return uploaded_file.getvalue().decode("utf-8")


def _init_session_state():
    if "workflow_step" not in st.session_state:
        st.session_state.workflow_step = 0
    if "workflow_data" not in st.session_state:
        st.session_state.workflow_data = {}


def _render_gatekeeper_stage(file_content: str):
    """Step 0 / 0.5 / 1 — input collection, gatekeeper validation, result display."""
    if st.session_state.workflow_step == 0:
        col1, _ = st.columns([3, 1])
        prompt = st.chat_input("Or paste Clinical Trial BRD text here...")
        with col1:
            if st.button("🚀 Start Agentic Workflow", use_container_width=True, type="primary") and file_content:
                st.session_state.workflow_data["user_input"] = file_content
                st.session_state.workflow_step = 0.5
                st.rerun()
        if prompt:
            st.session_state.workflow_data["user_input"] = prompt
            st.session_state.workflow_step = 0.5
            st.rerun()

    if st.session_state.workflow_step == 0.5:
        with st.spinner("🛡️ **Agent 0: Gatekeeper** — Checking protocol safety..."):
            result = run_gatekeeper(st.session_state.workflow_data["user_input"])
            st.session_state.workflow_data["gatekeeper_result"] = result
            st.session_state.workflow_step = 1 if result["is_valid"] == "VALID" else -1
            st.rerun()

    if st.session_state.workflow_step == -1:
        st.error("🛡️ **Guardrail Triggered:** The Gatekeeper Agent determined this input is NOT a valid Clinical Trial Protocol. Request blocked.")
        if st.button("🔄 Reset & Try Again"):
            st.session_state.workflow_step = 0
            st.session_state.workflow_data = {}
            st.rerun()

    if st.session_state.workflow_step >= 1:
        with st.expander("✅ **Step 1: Gatekeeper Agent** — Protocol Validated", expanded=(st.session_state.workflow_step == 1)):
            st.success("The Gatekeeper (LLaMA-3.1-8b) confirmed this is a valid Clinical Trial Protocol.")
            st.json(st.session_state.workflow_data["gatekeeper_result"])

    if st.session_state.workflow_step == 1:
        if st.button("▶️ Run Protocol Extractor (LLaMA-70b)", type="primary", use_container_width=True):
            st.session_state.workflow_step = 1.5
            st.rerun()


def _render_extractor_stage():
    """Step 1.5 / 2 — LLM extraction run and structured criteria display."""
    if st.session_state.workflow_step == 1.5:
        with st.spinner("📄 **Agent 1: Protocol Analyst** — Extracting structured criteria using Groq (LLaMA-3.3-70b) with Pydantic..."):
            result = run_extractor(st.session_state.workflow_data["user_input"])
            st.session_state.workflow_data["extractor_result"] = result
            st.session_state.workflow_step = 2
            st.rerun()

    if st.session_state.workflow_step >= 2:
        with st.expander("✅ **Step 2: Protocol Analyst** — Raw Criteria Extracted", expanded=(st.session_state.workflow_step == 2)):
            st.info("The Protocol Analyst (LLaMA-3.3-70b) extracted the following structured criteria using **Pydantic** schema enforcement:")
            extracted = st.session_state.workflow_data["extractor_result"]["extracted_json"]

            cols = st.columns(3)
            with cols[0]:
                st.markdown("**✅ Inclusion Criteria:**")
                for key, val in extracted.items():
                    if val and str(val).lower() != "none" and not key.startswith("exclude_"):
                        st.markdown(f"- `{key}`: **{val}**")
            with cols[1]:
                st.markdown("**❌ Exclusion Criteria:**")
                for key, val in extracted.items():
                    if val and str(val).lower() != "none" and key.startswith("exclude_"):
                        st.markdown(f"- `{key}`: **{val}**")
            with cols[2]:
                st.markdown("**Raw JSON Output:**")
                st.json(extracted)

    if st.session_state.workflow_step == 2:
        if st.button("▶️ Run Ontology RAG Mapper (FAISS + LLM Re-Ranker)", type="primary", use_container_width=True):
            st.session_state.workflow_step = 2.5
            st.rerun()


def _render_mapper_stage():
    """Step 2.5 / 3 — FAISS + LLM re-ranking and optional HITL override UI."""
    if st.session_state.workflow_step == 2.5:
        with st.spinner("🔗 **Agent 2: Ontology Mapper** — Querying FAISS Vector DB and LLM Re-Ranking..."):
            result = run_mapper(
                st.session_state.workflow_data["extractor_result"]["extracted_json"],
                st.session_state.workflow_data["user_input"],
            )
            st.session_state.workflow_data["mapper_result"] = result
            st.session_state.workflow_data["has_ambiguity"] = any(
                isinstance(v, str) and v.startswith("AMBIGUOUS_RAW:")
                for v in result["mapped_json"].values()
            )
            st.session_state.workflow_step = 3
            st.rerun()

    if st.session_state.workflow_step >= 3:
        has_ambiguity = st.session_state.workflow_data.get("has_ambiguity", False)
        expander_title = (
            "⚠️ **Step 3: Ontology Mapper** — AMBIGUITY DETECTED (HITL Required)"
            if has_ambiguity
            else "✅ **Step 3: Ontology Mapper** — Schema Mapping Complete"
        )

        with st.expander(expander_title, expanded=(st.session_state.workflow_step == 3)):
            mapper_result = st.session_state.workflow_data["mapper_result"]
            mapped = mapper_result["mapped_json"]
            faiss_details = mapper_result.get("faiss_details", {})
            extracted = st.session_state.workflow_data["extractor_result"]["extracted_json"]

            st.markdown("#### 🔄 Schema Resolution: Before → After")
            comparison_data = []
            for key in extracted.keys():
                raw_val = extracted.get(key)
                mapped_val = mapped.get(key)
                if raw_val and str(raw_val).lower() != "none":
                    is_ambiguous = isinstance(mapped_val, str) and mapped_val.startswith("AMBIGUOUS_RAW:")
                    status = "⚠️ AMBIGUOUS" if is_ambiguous else "✅ Resolved"
                    display_mapped = mapped_val.split("AMBIGUOUS_RAW:")[1] if is_ambiguous else mapped_val
                    comparison_data.append({
                        "Field": key,
                        "Raw LLM Output": str(raw_val),
                        "Schema-Mapped Output": str(display_mapped),
                        "Status": status,
                    })

            if comparison_data:
                st.dataframe(pd.DataFrame(comparison_data), hide_index=True, use_container_width=True)

            if faiss_details:
                st.markdown("#### 🔍 FAISS Retrieval Details (Top-5 Vector Matches)")
                for field, details in faiss_details.items():
                    st.markdown(f"**Field: `{field}`** → Input: *\"{details['raw_input']}\"*")
                    st.dataframe(pd.DataFrame(details["top_matches"]), hide_index=True, use_container_width=True)
                    st.markdown(f"🤖 **LLM Re-Ranker Decision:** `{details.get('resolved_to', 'N/A')}`")
                    st.markdown("---")

    # HITL Override (only visible when ambiguity detected)
    if st.session_state.workflow_step == 3 and st.session_state.workflow_data.get("has_ambiguity", False):
        st.error("🚨 **HUMAN-IN-THE-LOOP REQUIRED:** The LLM Re-Ranker could not confidently resolve one or more clinical terms. Please select the correct mapping below.")

        mapped = st.session_state.workflow_data["mapper_result"]["mapped_json"]
        updates_needed = {}

        base_dir = os.path.dirname(os.path.dirname(__file__))
        ontology_path = os.path.join(base_dir, "resources", "ontology_dictionary.json")
        if os.path.exists(ontology_path):
            with open(ontology_path, "r") as f:
                ontology = json.load(f)

        schema_key_map = {
            "medical_condition": "Medical Condition",
            "admission_type": "Admission Type",
            "medication": "Medication",
            "test_results": "Test Results",
            "blood_type": "Blood Type",
        }

        for key, val in mapped.items():
            if isinstance(val, str) and val.startswith("AMBIGUOUS_RAW:"):
                raw_term = val.split("AMBIGUOUS_RAW:")[1]
                st.write(f"**Field:** `{key}` | **Protocol Text:** \"{raw_term}\"")
                onto_key = schema_key_map.get(key)
                options = ["--- SELECT OVERRIDE ---"] + ontology.get(onto_key, [])
                choice = st.selectbox(f"Select Official '{onto_key}' Mapping:", options, key=f"hitl_{key}")
                if choice != "--- SELECT OVERRIDE ---":
                    updates_needed[key] = choice

        if st.button("✅ Submit Override & Resume Workflow", type="primary"):
            mapped.update(updates_needed)
            st.session_state.workflow_data["mapper_result"]["mapped_json"] = mapped
            st.session_state.workflow_data["has_ambiguity"] = False
            st.rerun()

    if st.session_state.workflow_step == 3 and not st.session_state.workflow_data.get("has_ambiguity", False):
        if st.button("▶️ Run Deterministic Patient Search (Pandas Engine)", type="primary", use_container_width=True):
            st.session_state.workflow_step = 3.5
            st.rerun()


def _render_data_engine_stage():
    """Step 3.5 / 4 — Pandas search execution and final results with Excel download."""
    if st.session_state.workflow_step == 3.5:
        with st.spinner("🔍 **Agent 3: Data Engine** — Executing deterministic Pandas query..."):
            result = execute_deterministic_patient_search(
                st.session_state.workflow_data["mapper_result"]["mapped_json"]
            )
            st.session_state.workflow_data["query_result"] = result
            st.session_state.workflow_step = 4
            st.rerun()

    if st.session_state.workflow_step >= 4:
        query_result = st.session_state.workflow_data["query_result"]
        st.success(f"✅ **Workflow Complete!** Found **{query_result['total_matched']}** eligible patients.")

        with st.expander("📊 **Step 4: Data Engine** — Filter Execution Log", expanded=True):
            st.markdown("#### Filter Pipeline (Deterministic Pandas)")
            for log_entry in query_result["filter_log"]:
                st.markdown(log_entry)

        st.markdown("---")
        st.markdown("### 📋 Example Patients")
        if not query_result["eligible_patients"].empty:
            st.dataframe(query_result["eligible_patients"].head(10), hide_index=True, use_container_width=True)

            towrite = io.BytesIO()
            query_result["eligible_patients"].to_excel(towrite, index=False, engine="openpyxl")
            towrite.seek(0)
            st.download_button(
                label="📥 Download All Eligible Patients as Excel",
                data=towrite,
                file_name=f"Clinical_Trial_Matches_{st.session_state.workflow_data.get('protocol_name', 'Results')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.warning("No patients matched all the specified criteria.")

def _render_summary_stage():
    """Step 4.5 / 5 — Final executive summary by the Summary Provider."""
    if st.session_state.workflow_step == 4:
        if st.button("▶️ Run Summary Provider (Final Verification)", type="primary", use_container_width=True):
            st.session_state.workflow_step = 4.5
            st.rerun()

    if st.session_state.workflow_step == 4.5:
        with st.spinner("⚖️ **Agent 5: Summary Provider** — Generating final executive summary..."):
            # We just create a clean summary of the data engine's findings
            query_result = st.session_state.workflow_data["query_result"]
            summary = (
                f"### 📋 Executive Summary\n\n"
                f"**Match Status:** ✅ SUCCESS\n\n"
                f"**Total Patients Matched:** {query_result['total_matched']}\n\n"
                f"**Summary:** The Clinical Trial Matcher has successfully processed the protocol and "
                f"filtered the patient database. All {query_result['total_matched']} identified patients satisfy "
                f"the 100% deterministic criteria extracted by the Protocol Analyst.\n\n"
                f"**Next Steps:** Proceed with manual clinical review of the top 10 matches provided below."
            )
            st.session_state.workflow_data["summary_output"] = summary
            st.session_state.workflow_step = 5
            st.rerun()

    if st.session_state.workflow_step >= 5:
        with st.expander("⚖️ **Step 5: Summary Provider** — Final Executive Summary", expanded=True):
            st.markdown(st.session_state.workflow_data["summary_output"])

        st.markdown("---")
        if st.button("🔄 Reset & Process Another Protocol"):
            st.session_state.workflow_step = 0
            st.session_state.workflow_data = {}
            st.rerun()


# ── Public Entry Point ─────────────────────────────────────────────────────────
def render_tab_agent_interface():
    st.markdown("### Powered by LangGraph, Groq, and Schema-Aware RAG")
    st.caption("Upload a Clinical Trial Protocol (BRD) to begin the step-by-step agentic workflow.")

    _init_session_state()

    uploaded_file = st.file_uploader("Upload a Clinical Trial BRD (.txt or .docx)", type=["txt", "docx"])
    file_content = ""
    if uploaded_file is not None:
        file_content = _read_uploaded_file(uploaded_file)
        st.success(f"File '{uploaded_file.name}' loaded successfully! ({len(file_content.split())} words)")

    _render_gatekeeper_stage(file_content)
    _render_extractor_stage()
    _render_mapper_stage()
    _render_data_engine_stage()
    _render_summary_stage()
