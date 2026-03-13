import streamlit as st
import pandas as pd
import os
import json
import docx
from agent import run_gatekeeper, run_extractor, run_mapper, run_query

st.set_page_config(page_title="Agilisium PoC: Clinical Trial Agent", layout="wide")

st.title("🧬 AI Clinical Trial Patient Matcher")

# Sidebar: Sample Document Downloads
with st.sidebar:
    st.header("📂 Sample Protocols")
    st.markdown("Download these sample BRDs to test the agent workflow.")
    
    import requests
    samples = [
        {"name": "BRD 1: Straightforward (Exact)", "url": "https://clinicaldata-765366202501-ap-southeast-2-an.s3.ap-southeast-2.amazonaws.com/BRD+1.docx"},
        {"name": "BRD 2: Semantic (Language)", "url": "https://clinicaldata-765366202501-ap-southeast-2-an.s3.ap-southeast-2.amazonaws.com/BRD+2.docx"},
        {"name": "BRD 3: HITL (Condition Ambiguity)", "url": "https://clinicaldata-765366202501-ap-southeast-2-an.s3.ap-southeast-2.amazonaws.com/BRD+3.docx"},
        {"name": "BRD 4: HITL (Medication Ambiguity)", "url": "https://clinicaldata-765366202501-ap-southeast-2-an.s3.ap-southeast-2.amazonaws.com/BRD+4.docx"},
    ]
    
    for sample in samples:
        try:
            response = requests.get(sample["url"])
            if response.status_code == 200:
                file_name = sample["url"].split("/")[-1].replace("+", " ")
                st.download_button(
                    label=f"📥 {sample['name']}",
                    data=response.content,
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
        except Exception as e:
            st.error(f"Could not load {sample['name']} from S3: {e}")
    st.divider()
    st.info("💡 **Tip:** After downloading, upload the file in the 'Agent Interface' tab to see the agentic magic.")

# Create Tabs for the UI
tab1, tab2, tab3 = st.tabs(["✨ Agent Interface", "📊 Data Overview (Phase 0)", "🏛️ Architecture Workflow"])

with tab1:
    st.markdown("### Powered by LangGraph, Groq, and Schema-Aware RAG")
    st.caption("Upload a Clinical Trial Protocol (BRD) to begin the step-by-step agentic workflow.")

    # Initialize session state for the step-by-step workflow
    if "workflow_step" not in st.session_state:
        st.session_state.workflow_step = 0  # 0 = waiting, 1 = gatekeeper done, 2 = extractor done, 3 = mapper done, 4 = query done
    if "workflow_data" not in st.session_state:
        st.session_state.workflow_data = {}

    # File Uploader
    uploaded_file = st.file_uploader("Upload a Clinical Trial BRD (.txt or .docx)", type=["txt", "docx"])
    
    file_content = ""
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".docx"):
            doc = docx.Document(uploaded_file)
            file_content = "\n".join([para.text for para in doc.paragraphs])
        else:
            file_content = uploaded_file.getvalue().decode("utf-8")
            
        st.success(f"File '{uploaded_file.name}' loaded successfully! ({len(file_content.split())} words)")

    # =====================================================================
    # STEP 0: Start the Workflow
    # =====================================================================
    if st.session_state.workflow_step == 0:
        col1, col2 = st.columns([3, 1])
        
        prompt = st.chat_input("Or paste Clinical Trial BRD text here...")
        
        with col1:
            if st.button("🚀 Start Agentic Workflow", use_container_width=True, type="primary") and file_content:
                st.session_state.workflow_data["user_input"] = file_content
                st.session_state.workflow_step = 0.5  # Trigger gatekeeper
                st.rerun()
        
        if prompt:
            st.session_state.workflow_data["user_input"] = prompt
            st.session_state.workflow_step = 0.5
            st.rerun()

    # =====================================================================
    # STEP 0.5: Run Gatekeeper
    # =====================================================================
    if st.session_state.workflow_step == 0.5:
        with st.spinner("🛡️ **Agent 0: Gatekeeper** — Checking protocol safety..."):
            result = run_gatekeeper(st.session_state.workflow_data["user_input"])
            st.session_state.workflow_data["gatekeeper_result"] = result
            
            if result["is_valid"] == "VALID":
                st.session_state.workflow_step = 1
            else:
                st.session_state.workflow_step = -1  # Blocked
            st.rerun()

    # =====================================================================
    # BLOCKED STATE
    # =====================================================================
    if st.session_state.workflow_step == -1:
        st.error("🛡️ **Guardrail Triggered:** The Gatekeeper Agent determined this input is NOT a valid Clinical Trial Protocol. Request blocked.")
        if st.button("🔄 Reset & Try Again"):
            st.session_state.workflow_step = 0
            st.session_state.workflow_data = {}
            st.rerun()

    # =====================================================================
    # STEP 1: Gatekeeper Passed — Show result & offer next step
    # =====================================================================
    if st.session_state.workflow_step >= 1:
        with st.expander("✅ **Step 1: Gatekeeper Agent** — Protocol Validated", expanded=(st.session_state.workflow_step == 1)):
            st.success("The Gatekeeper (LLaMA-3.1-8b) confirmed this is a valid Clinical Trial Protocol.")
            st.json(st.session_state.workflow_data["gatekeeper_result"])
    
    if st.session_state.workflow_step == 1:
        if st.button("▶️ Run Protocol Extractor (LLaMA-70b)", type="primary", use_container_width=True):
            st.session_state.workflow_step = 1.5
            st.rerun()

    # =====================================================================
    # STEP 1.5: Run Extractor
    # =====================================================================
    if st.session_state.workflow_step == 1.5:
        with st.spinner("📄 **Agent 1: Protocol Analyst** — Extracting structured criteria using Groq (LLaMA-3.3-70b) with Pydantic..."):
            result = run_extractor(st.session_state.workflow_data["user_input"])
            st.session_state.workflow_data["extractor_result"] = result
            st.session_state.workflow_step = 2
            st.rerun()

    # =====================================================================
    # STEP 2: Extractor Done — Show extracted JSON
    # =====================================================================
    if st.session_state.workflow_step >= 2:
        with st.expander("✅ **Step 2: Protocol Analyst** — Raw Criteria Extracted", expanded=(st.session_state.workflow_step == 2)):
            st.info("The Protocol Analyst (LLaMA-3.3-70b) extracted the following structured criteria using **Pydantic** schema enforcement:")
            extracted = st.session_state.workflow_data["extractor_result"]["extracted_json"]
            
            cols = st.columns(3)
            with cols[0]:
                st.markdown("**✅ Inclusion Criteria:**")
                for k, v in extracted.items():
                    if v and str(v).lower() != 'none' and not k.startswith("exclude_"):
                        st.markdown(f"- `{k}`: **{v}**")
            with cols[1]:
                st.markdown("**❌ Exclusion Criteria:**")
                for k, v in extracted.items():
                    if v and str(v).lower() != 'none' and k.startswith("exclude_"):
                        st.markdown(f"- `{k}`: **{v}**")
            with cols[2]:
                st.markdown("**Raw JSON Output:**")
                st.json(extracted)
    
    if st.session_state.workflow_step == 2:
        if st.button("▶️ Run Ontology RAG Mapper (FAISS + LLM Re-Ranker)", type="primary", use_container_width=True):
            st.session_state.workflow_step = 2.5
            st.rerun()

    # =====================================================================
    # STEP 2.5: Run Mapper
    # =====================================================================
    if st.session_state.workflow_step == 2.5:
        with st.spinner("🔗 **Agent 2: Ontology Mapper** — Querying FAISS Vector DB and LLM Re-Ranking..."):
            result = run_mapper(
                st.session_state.workflow_data["extractor_result"]["extracted_json"],
                st.session_state.workflow_data["user_input"]
            )
            st.session_state.workflow_data["mapper_result"] = result
            
            # Check if any fields are AMBIGUOUS
            has_ambiguity = any(
                isinstance(v, str) and v.startswith("AMBIGUOUS_RAW:") 
                for v in result["mapped_json"].values()
            )
            st.session_state.workflow_data["has_ambiguity"] = has_ambiguity
            st.session_state.workflow_step = 3
            st.rerun()

    # =====================================================================
    # STEP 3: Mapper Done — Show mapped results with FAISS details
    # =====================================================================
    if st.session_state.workflow_step >= 3:
        has_ambiguity = st.session_state.workflow_data.get("has_ambiguity", False)
        
        expander_title = "⚠️ **Step 3: Ontology Mapper** — AMBIGUITY DETECTED (HITL Required)" if has_ambiguity else "✅ **Step 3: Ontology Mapper** — Schema Mapping Complete"
        
        with st.expander(expander_title, expanded=(st.session_state.workflow_step == 3)):
            mapper_result = st.session_state.workflow_data["mapper_result"]
            mapped = mapper_result["mapped_json"]
            faiss_details = mapper_result.get("faiss_details", {})
            
            extracted = st.session_state.workflow_data["extractor_result"]["extracted_json"]
            
            # Show Before vs After comparison table
            st.markdown("#### 🔄 Schema Resolution: Before → After")
            comparison_data = []
            for k in extracted.keys():
                raw_val = extracted.get(k)
                mapped_val = mapped.get(k)
                if raw_val and str(raw_val).lower() != 'none':
                    status = "⚠️ AMBIGUOUS" if isinstance(mapped_val, str) and mapped_val.startswith("AMBIGUOUS_RAW:") else "✅ Resolved"
                    display_mapped = mapped_val.split("AMBIGUOUS_RAW:")[1] if isinstance(mapped_val, str) and mapped_val.startswith("AMBIGUOUS_RAW:") else mapped_val
                    comparison_data.append({
                        "Field": k,
                        "Raw LLM Output": str(raw_val),
                        "Schema-Mapped Output": str(display_mapped),
                        "Status": status
                    })
            
            if comparison_data:
                st.dataframe(pd.DataFrame(comparison_data), hide_index=True, use_container_width=True)
            
            # Show FAISS retrieval details
            if faiss_details:
                st.markdown("#### 🔍 FAISS Retrieval Details (Top-5 Vector Matches)")
                for field, details in faiss_details.items():
                    st.markdown(f"**Field: `{field}`** → Input: *\"{details['raw_input']}\"*")
                    matches_df = pd.DataFrame(details["top_matches"])
                    st.dataframe(matches_df, hide_index=True, use_container_width=True)
                    st.markdown(f"🤖 **LLM Re-Ranker Decision:** `{details.get('resolved_to', 'N/A')}`")
                    st.markdown("---")
    
    # =====================================================================
    # STEP 3: HITL Override UI (if ambiguous)
    # =====================================================================
    if st.session_state.workflow_step == 3 and st.session_state.workflow_data.get("has_ambiguity", False):
        st.error("🚨 **HUMAN-IN-THE-LOOP REQUIRED:** The LLM Re-Ranker could not confidently resolve one or more clinical terms. Please select the correct mapping below.")
        
        mapped = st.session_state.workflow_data["mapper_result"]["mapped_json"]
        updates_needed = {}
        
        ontology_path = os.path.join(os.path.dirname(__file__), "ontology_dictionary.json")
        if os.path.exists(ontology_path):
            with open(ontology_path, 'r') as f:
                ontology = json.load(f)
        
        schema_key_map = {
            "medical_condition": "Medical Condition",
            "admission_type": "Admission Type",
            "medication": "Medication",
            "test_results": "Test Results",
            "blood_type": "Blood Type"
        }
        
        for k, v in mapped.items():
            if isinstance(v, str) and v.startswith("AMBIGUOUS_RAW:"):
                raw_term = v.split("AMBIGUOUS_RAW:")[1]
                st.write(f"**Field:** `{k}` | **Protocol Text:** \"{raw_term}\"")
                
                onto_key = schema_key_map.get(k)
                options = ontology.get(onto_key, [])
                options_with_placeholder = ["--- SELECT OVERRIDE ---"] + options
                
                choice = st.selectbox(f"Select Official '{onto_key}' Mapping:", options_with_placeholder, key=f"hitl_{k}")
                if choice != "--- SELECT OVERRIDE ---":
                    updates_needed[k] = choice
        
        if st.button("✅ Submit Override & Resume Workflow", type="primary"):
            mapped.update(updates_needed)
            st.session_state.workflow_data["mapper_result"]["mapped_json"] = mapped
            st.session_state.workflow_data["has_ambiguity"] = False
            st.rerun()
    
    # =====================================================================
    # STEP 3: Proceed to Query (No ambiguity or resolved)
    # =====================================================================
    if st.session_state.workflow_step == 3 and not st.session_state.workflow_data.get("has_ambiguity", False):
        if st.button("▶️ Run Deterministic Patient Search (Pandas Engine)", type="primary", use_container_width=True):
            st.session_state.workflow_step = 3.5
            st.rerun()

    # =====================================================================
    # STEP 3.5: Run Query
    # =====================================================================
    if st.session_state.workflow_step == 3.5:
        with st.spinner("🔍 **Agent 3: Data Engine** — Executing deterministic Pandas query..."):
            result = run_query(st.session_state.workflow_data["mapper_result"]["mapped_json"])
            st.session_state.workflow_data["query_result"] = result
            st.session_state.workflow_step = 4
            st.rerun()

    # =====================================================================
    # STEP 4: Final Results
    # =====================================================================
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
            # Display only top 10 in UI
            st.dataframe(query_result["eligible_patients"].head(10), hide_index=True, use_container_width=True)
            
            # --- Excel Download Logic ---
            import io
            towrite = io.BytesIO()
            query_result["eligible_patients"].to_excel(towrite, index=False, engine='openpyxl')
            towrite.seek(0)
            
            st.download_button(
                label="📥 Download All Eligible Patients as Excel",
                data=towrite,
                file_name=f"Clinical_Trial_Matches_{st.session_state.workflow_data.get('protocol_name', 'Results')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("No patients matched all the specified criteria.")
        
        st.markdown("---")
        if st.button("🔄 Reset & Process Another Protocol"):
            st.session_state.workflow_step = 0
            st.session_state.workflow_data = {}
            st.rerun()

with tab2:
    st.markdown("## 📊 Database Profiling & Cleaning (Phase 0)")
    st.markdown("Before the LangGraph agents are invoked, the system executes a lightning-fast Pandas query across the patient records to extract the unique schema values and clean anomalies.")
    
    # Load Data
    db_path = "https://clinicaldata-765366202501-ap-southeast-2-an.s3.ap-southeast-2.amazonaws.com/healthcare_dataset.csv"
    cleaned_db_path = "https://clinicaldata-765366202501-ap-southeast-2-an.s3.ap-southeast-2.amazonaws.com/healthcare_dataset_cleaned.csv"
    ontology_path = os.path.join(os.path.dirname(__file__), "ontology_dictionary.json")

    try:
        df_raw = pd.read_csv(db_path)
        df_clean = pd.read_csv(cleaned_db_path)
        data_loaded = True
    except Exception as e:
        data_loaded = False
        st.error(f"Failed to load dataset from S3: {e}")

    if data_loaded:

        col1, col2, col3 = st.columns(3)
        col1.metric("Raw Patient Records", len(df_raw))
        col2.metric("Cleaned Patient Records", len(df_clean))
        col3.metric("Anomalies Removed/Fixed", len(df_raw) - len(df_clean) + 108)
        
        st.divider()
        
        st.markdown("### 🧬 The Ontology Dictionary (Schema-Aware RAG)")
        st.markdown("This dictionary is extracted instantaneously by Pandas and embedded into the **FAISS Vector Database**.")
        if os.path.exists(ontology_path):
            with open(ontology_path, 'r') as f:
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
    else:
        st.warning("Database files not found. Please run `clean_database.py` first.")

with tab3:
    st.markdown("## 🏛️ System Architecture")
    st.markdown("This proof-of-concept leverages a **Multi-Agent LangGraph** workflow to accurately match patients to clinical trials while avoiding LLM hallucinations.")
    
    st.markdown("### 🤖 Agent Roles & Responsibilities")
    st.markdown('''
    - **🛡️ Gatekeeper (LLaMA-3.1-8b):** Red-team defense. Rejects generic chat/hallucination attempts.
    - **📄 Protocol Analyst (LLaMA-3.3-70b):** Extracts structured criteria using Pydantic schema enforcement.
    - **🔗 Ontology Mapper (FAISS + LLM Re-Ranker):** Resolves raw clinical text to official database keys via Vector RAG.
    - **🔍 Data Engine (Pandas):** 100% deterministic filtering with exact equality matches.
    - **⚖️ Auditor:** Verifies constraints and formats the final executive summary.
    ''')
    
    st.markdown("### 🔀 Workflow Diagram")
    mermaid_code = """
    graph TD
        User[User Input: Protocol/BRD] --> Gatekeeper{Gatekeeper Node}
        Gatekeeper -- Invalid --> Error[Error Node: Block Request]
        Gatekeeper -- Valid --> Extractor[Protocol Analyst: Pydantic Extraction]
        Extractor --> Mapper[Ontology Mapper: FAISS + LLM Re-Ranker]
        Mapper -- Confident --> DataEngine[Data Engine: Deterministic Pandas Query]
        Mapper -- Ambiguous --> HITL[Human-In-The-Loop: Manual Override]
        HITL --> DataEngine
        DataEngine --> Auditor[Auditor Node: Validation]
        Auditor --> Final[Final Executive Summary]
        Error --> Final
    """
    st.markdown(f"```mermaid\n{mermaid_code}\n```")
    st.info("The application implements built-in API rate limiting (respecting free-tier limits) and robust conditional routing to ensure production-grade reliability.")
