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

    st.markdown("## 🖼️ Architecture Overview")
    st.markdown(
        "The system operates as a pipeline of specialized agents, each designed for a specific task "
        "to ensure optimal performance, low cost, and high accuracy."
    )

    # Render the architecture diagram image (centered and constrained)
    base_dir = os.path.dirname(os.path.dirname(__file__))
    img_path = os.path.join(base_dir, "architecture_diagram.png")
    if os.path.exists(img_path):
        col1, col2, col3 = st.columns([1, 4, 1])
        with col2:
            st.image(img_path, use_column_width=True)
    else:
        st.warning("architecture_diagram.png not found in project root.")

    st.divider()

    st.markdown("## 🤖 Agent Roles & Responsibilities")
    st.markdown("""
1. **🛡️ Gatekeeper (LLaMA-3.1-8b):** The frontline defense. Acts as a semantic router — instantly rejects generic chat, off-topic questions, or prompt injection attempts before they consume any compute resources.

2. **📄 Protocol Analyst (LLaMA-3.3-70b):** The heavy-lifter. Reads dense, unstructured clinical BRD text and extracts exact inclusion/exclusion criteria. Uses **Pydantic schema enforcement** (`with_structured_output`) to guarantee correctly formatted downstream payloads.

3. **🔗 Ontology Mapper (FAISS + LLM Re-Ranker):** The translator. Bridges the gap between messy real-world medical text (e.g., *"High BP"*) and official database keys (e.g., *"Hypertension"*) via FAISS vector similarity + LLM re-ranking.

4. **🔍 Data Engine (Pandas):** The source of truth. LLMs *never* touch patient data directly. The mapped criteria are handed off to a deterministic Pandas engine — guaranteeing 100% data accuracy with zero hallucinated records.

5. **⚖️ Auditor:** The final check. Verifies constraints were met and formats the output into a clean human-readable executive summary.
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
**The Problem:** Sequential multi-LLM calls (Gatekeeper → Extractor → Mapper) exhausted Groq's free-tier RPM/TPM limits.

**The Fix:**
- **Gatekeeper** fails fast on bad input, saving tokens.
- **`@retry` with exponential backoff** (`tenacity`) gracefully handles quota resets.
- **Context Truncation** (`get_safe_document_context`) prevents oversized documents from hitting the context window limit.
""")

    with st.expander("Challenge 3: Structured Output Failures (BadRequestError)", expanded=False):
        st.markdown("""
**The Problem:** For complex BRDs, the 70b model would occasionally fail to return valid JSON fitting the Pydantic schema.

**The Fix:**
- Made every field in `ClinicalCriteria` `Optional[]` — giving the LLM permission to leave missing criteria blank.
- Added a `try-except` fallback that returns an empty schema instead of crashing the pipeline.
- Switched to `llama-3.3-70b-versatile` for more reliable structured output on the free tier.
""")

    with st.expander("Challenge 4: EC2 Deployment — 'No space left on device'", expanded=False):
        st.markdown("""
**The Problem:** Docker builds on the free-tier EC2 t2.micro (8GB EBS) repeatedly ran out of disk space.

**The Fix:**
- Switched to the CPU-only PyTorch build (`--extra-index-url https://download.pytorch.org/whl/cpu`), reducing library size from ~3GB to ~150MB.
- Moved all large data files (CSV database, BRD documents) to **AWS S3**, fetched via HTTP at runtime rather than bundled in the Docker image.
""")

    st.divider()

    st.markdown("## 🧠 Key Learnings & Takeaways")
    st.markdown("""
1. **Multi-Agent Orchestration:** LangGraph makes complex AI workflows infinitely more debuggable and reliable than a single massive prompt.

2. **Hybrid Determinism:** The future of Enterprise AI is LLMs as *translators* powering traditional, deterministic code — not replacing it.

3. **Cloud Infrastructure & Optimization:** Hunting down bloated dependencies (like GPU drivers in PyTorch) and leveraging S3 for data separation are real-world production skills.

4. **Resilience over Raw Performance:** In a multi-step agentic workflow, a timeout at step 4 ruins the entire experience. Retry logic is just as critical as the core AI prompts.

---
*This project evolved from a simple scripted prompt into a resilient, cloud-deployed, multi-agent AI architecture capable of real-world clinical application.*
""")
