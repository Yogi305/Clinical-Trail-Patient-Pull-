# Workflow Changes Analysis: AI Clinical Trial Patient Matcher

This document details the architectural and workflow changes required to transition the current codebase to the architecture proposed in the **NEW Product Requirements Document (PRD)**.

## 1. Current Implementation vs. Proposed Architecture

The current implementation (`agent.py` and `app.py`) relies on a 4-node LangGraph workflow that uses an LLM to extract JSON criteria, followed by a Pandas engine that relies heavily on fuzzy matching (`.str.contains`, `in`, etc.) to compensate for semantic differences between the unstructured trial protocols and the structured database schema.

The **NEW PRD** introduces a "Schema-Aware RAG Architecture" to solve this semantic gap explicitly, completely removing "fuzzy math" from the data retrieval layer to guarantee zero clinical hallucinations.

---

## 2. Detailed Workflow Changes by Phase / Node

### ⚙️ Phase 0: System Initialization (NEW)
- **Current State:** The CSV database is simply loaded into memory as a Pandas DataFrame on module start.
- **New Requirement:** Add a startup sequence before LangGraph initializes. 
- **Action Required:** Use Pandas to extract all unique categorical schema values (e.g., all unique diseases in the `Medical Condition` column) and build a **FAISS Vector Database (Ontology DB)**. This ensures RAG only queries an official data dictionary instead of raw patient records.

### 🛡️ Node 0: The Gatekeeper
- **Current State:** Implemented and functional. Uses LLaMA-3 (8b) to block prompt injections and non-clinical requests.
- **New Requirement:** No major changes required; keep the existing routing logic.

### 📄 Node 1: Clinical Protocol Extractor (UPDATED)
- **Current State:** Prompts the LLM to output JSON and relies on manual string manipulation/`json.loads()` and `try/except` fallbacks to parse the criteria.
- **New Requirement:**
  1. **Long-Context / Few-Shot Optimization:** Update the prompt to aggressively ignore irrelevant sections ("Background", "Methodology").
  2. **Strict Pydantic Enforcement:** Replace the manual JSON parsing with strict Langchain structured output wrappers using Pydantic models. This forces the LLM to yield the exact required schema to constrain hallucinations. 
  3. **Output Change:** Yields "raw", cleanly structured JSON containing *unstandardized* clinical terms based on the document text.

### 🔀 Node 2: Schema-Aware Ontology Mapper (NEW)
- **Current State:** Does not exist. (The current codebase skips directly to querying).
- **New Requirement:** Insert a new LangGraph Node that acts as an Entity Resolver/Medical Coder.
- **Action Required:**
  1. Takes the raw output from Node 1.
  2. **Top-K RAG:** Queries the FAISS Ontology DB (created in Phase 0) with the raw conditions using Cosine Similarity (k=5).
  3. **LLM Re-Ranking:** Uses an LLM to evaluate the Top 5 FAISS matches in context and select the perfect clinical equivalent.
  4. **Human-In-The-Loop (HITL):** Introduce an interrupt in LangGraph for ambiguous cases, pushing a flag to the Streamlit UI for manual clinician selection before proceeding.

### 📊 Node 3: Deterministic Data Engine (UPDATED)
- **Current State:** (Currently Node 3 / `query_node` in `agent.py`). Relies heavily on fuzzy string matching (`str.contains`, case-insensitive substring search) because the LLM terms don't perfectly match the CSV terms.
- **New Requirement:** 
  - **Action Required:** Rewrite the Pandas filtering logic to be 100% deterministic mathematical bounds. Remove all `.str.contains` logic for categorical data. Because Node 2 perfectly standardize the parameters, the Data Engine must only execute exact strict-bounded SQL/Pandas equality (e.g., `df['Medical_Condition'] == criteria['medical_condition']`).

### ⚖️ Node 4: The Auditor (UPDATED)
- **Current State:** Formats a hardcoded summary text of the Top 5 Matched IDs.
- **New Requirement:** Maintain formatting role, but enforce an independent validation check to ensure no logical fallacies occurred before generating the UI summary.

---

## 3. Technology Stack Additions
To support these workflow changes, the following dependencies will need to be integrated into `requirements.txt` and the codebase:
- **FAISS (`faiss-cpu`)**: For building the local Ontology Vector Database.
- **HuggingFace Embeddings (`sentence-transformers`)**: Specifically `all-MiniLM-L6-v2` for generating the vector embeddings.
- **Pydantic**: For strict LLM output structure enforcement in Node 1.
- **LangGraph Checkpointing**: To manage the Stateful Human-In-The-Loop (HITL) pause in Node 2.

## 4. Summary of Impact
The fundamental shift is decoupling **Extraction** (Node 1) from **Resolution** (Node 2) and **Execution** (Node 3). By doing this, the system guarantees that the Pandas execution step remains purely deterministic and blazingly fast, moving all semantic reasoning strictly into the LLM/RAG layers where it belongs.
