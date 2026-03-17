"""
ui/tab_architecture.py
----------------------
Renders Tab 3: Architecture Workflow.

All content is rendered inline — no external markdown file dependency.
The architecture_diagram.png is loaded from the project root.
"""

import os
import streamlit as st


def render_tab_architecture():
    st.markdown("# 🏛️ Clinical Trial Patient Matcher: System Architecture & Journey")
    st.markdown(
        "Welcome to the deep dive of the **Clinical Trial Patient Matcher**. "
        "This project is a proof-of-concept that leverages a Multi-Agent LangGraph workflow to accurately match "
        "patients to clinical trials. Its defining feature is a hybrid approach combining large language models "
        "(LLMs) for complex reasoning with deterministic data engines to **eliminate AI hallucinations**."
    )



    st.divider()

    st.markdown("## 🤖 Agent Roles & Responsibilities")
    st.markdown("""
1. **🛡️ Gatekeeper (LLaMA-3.1-8b):** The frontline defense. Acts as a semantic router — instantly rejects generic chat, off-topic questions, or prompt injection attempts before they consume any compute resources.

2. **📄 Protocol Analyst (LLaMA-3.3-70b):** The heavy-lifter. Reads dense, unstructured clinical BRD text and extracts exact inclusion/exclusion criteria. Uses **Pydantic schema enforcement** (`with_structured_output`) to guarantee correctly formatted downstream payloads.

3. **🔗 Ontology Mapper (FAISS + LLM Re-Ranker):** The translator. Bridges the gap between messy real-world medical text (e.g., *"High BP"*) and official database keys (e.g., *"Hypertension"*) via FAISS vector similarity + LLM re-ranking.

4. **🔍 Data Engine (Pandas):** The source of truth. LLMs *never* touch patient data directly. The mapped criteria are handed off to a deterministic Pandas engine — guaranteeing 100% data accuracy with zero hallucinated records.

5. **⚖️ Summary Provider:** The final check. Verifies constraints were met and formats the output into a clean human-readable executive summary.
""")

    st.divider()

    st.markdown("## 🧗 Challenges Faced & How I Solved Them")

    with st.expander("Challenge 1: LLM Hallucinations in Patient Data", expanded=False):
        st.markdown("""
**The Problem:** When asked to *"find patients over 50 with Diabetes,"* the LLM would hallucinate records, return patients who were 49, or generate broken queries.

**The Fix:** Completely separated reasoning from execution. LLMs are *only* used for reading text and structuring parameters. The actual patient search is delegated to a rigid, deterministic Pandas script.
""")

    with st.expander("Challenge 2: API Rate Limits and Cloud Quotas", expanded=False):
        st.markdown("""
**The Problem:** Attempting to process complex protocols with a single massive API call exhausted Groq's free-tier Request-Per-Minute (RPM) and Token-Per-Minute (TPM) limits.

**The Fix:**
- **Atomic Agent Requests:** Re-architected the workflow to make **individual API calls for each agent request** (Gatekeeper, Extractor, Mapper). This distributes the load and prevents hitting hard caps.
""")



    st.divider()

    st.markdown("## 🧠 Key Learnings & Takeaways")
    st.markdown("""
1. **Multi-Agent Orchestration:** LangGraph makes complex AI workflows infinitely more debuggable and reliable than a single massive prompt.

2. **Hybrid Determinism:** The future of Enterprise AI is LLMs as *translators* powering traditional, deterministic code — not replacing it.

3. **Cloud Infrastructure & Optimization:** Hunting down bloated dependencies (like GPU drivers in PyTorch) and leveraging S3 for data separation are real-world production skills.

---
*This project evolved from a simple scripted prompt into a resilient, cloud-deployed, multi-agent AI architecture capable of real-world clinical application.*
""")
