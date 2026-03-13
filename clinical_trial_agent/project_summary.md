# 🧬 Enterprise AI Clinical Trial Patient Matcher Pipeline

## 🎯 Project Overview & Objective
This repository contains a Proof-of-Concept (PoC) AI Agent workflow designed to automate complex patient matching for clinical trials. Designed as a production-grade enterprise system, it moves beyond a naive Retrieval-Augmented Generation (RAG) framework (which is often prone to hallucinations and non-compliant operations) and instead implements a **Stateful Agentic Architecture** analogous to Life Sciences & Pharma "Molecule-to-Market" IT patterns.

## 🏗️ Architecture Stack
The tech stack operates on **Python**, **Streamlit** (for quick interactive frontend presentation), **LangGraph** (for graph-based stateful agent choreography), and **Langchain** + **Groq** for high-speed, scalable LLM reasoning (leveraging Llama3 capabilities).

### **The Multi-Agent Workflow (Nodes)**

The LangGraph orchestration uses multiple specific "Agent Nodes" to handle the data responsibly:

1. **🛡️ Node 0 - The Gatekeeper Agent (Semantic Router / Red-Team Guardrail):**
   - **Role:** Security, Compliance, and Guardrail.
   - **Action:** Inspects user prompts immediately. If the prompt is a general knowledge question, prompt injection attempt, or irrelevant question, the Gatekeeper rejects the request to prevent hallucination or misuse, routing to an Error Node.

2. **🧠 Node 1 - The Protocol Analyst (Reasoning Engine / Planner):**
   - **Role:** Medical and Data Abstraction.
   - **Action:** Parses verbose, human-readable Clinical Trial BRDs (Business Requirement Documents) or protocols and distills complex inclusion and exclusion clauses strictly into a structured key-value format (JSON) that upstream systems can predictably query.

3. **🔍 Node 2 - Data Query Pipeline (Hybrid Search Engine):**
   - **Role:** Execution & Integration.
   - **Action:** Interfaces directly with patient health data (a synthesized database via `pandas`). It filters against strict medical boundaries (e.g., Age ranges, test results, gender, specific biomarkers) and queries matching patient IDs.

4. **⚖️ Node 3 - The Auditor Layer (Validation):**
   - **Role:** Quality Assurance & Output formatting.
   - **Action:** Gathers the output from the data query phase and provides an executive patient match summary. In large-scale systems, this node would cross-reference findings to double-check that matched IDs legally belong to an anonymized trial pool and securely present only verified data.

## 💡 Why This Matters (The "Wow" Factor)
1. **Multi-Model Orchestration:** Not all tasks require the same level of intelligence. This system explicitly utilizes a **Multi-LLM Strategy**. It routing nodes (like the Gatekeeper) use highly efficient, low-latency models (e.g., `llama3-8b`) to save costs and reduce inference time, while heavy parsing tasks (like Protocol Analysis) leverage high-parameter reasoning models (e.g., `llama3-70b`) to guarantee accuracy and strict JSON adherence.
2. **Enterprise Readiness:** This system mirrors enterprise-scale software because it focuses on **determinism, structured outputs, and explicit error handling** rather than assuming a single giant text-generation prompt logic will succeed. It shows a deep understanding of evaluating metrics, mitigating risks, understanding clinical constraints, and defending against real-world LLM adoption hurdles.
