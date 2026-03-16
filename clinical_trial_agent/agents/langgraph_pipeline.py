"""
agents/langgraph_pipeline.py
----------------------------
LangGraph StateGraph definition.

Wires all agent nodes into a stateful directed graph for reference and
potential future use (e.g., running the full pipeline in one shot via CLI).
The Streamlit UI calls each agent's standalone function directly instead of
running this full pipeline, giving finer control over the step-by-step display.
"""

from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END

from agents.gatekeeper import run_gatekeeper
from agents.extractor import run_extractor
from agents.mapper import run_mapper
from agents.data_engine import execute_deterministic_patient_search


# ── Shared State Schema ────────────────────────────────────────────────────────
class AgentState(TypedDict):
    user_input: str
    is_valid: str
    extracted_json: Dict[str, Any]
    mapped_json: Dict[str, Any]
    eligible_patients: str
    final_output: str


# ── Individual Node Wrappers ───────────────────────────────────────────────────
def gatekeeper_node(state: AgentState):
    return run_gatekeeper(state["user_input"])

def error_node(state: AgentState):
    return {
        "final_output": (
            "🛡️ **Guardrail Triggered:** I am a specialized Clinical Trial AI. "
            "I can only process Clinical Trial Protocols and Business Requirement Documents. "
            "Request blocked."
        )
    }

def extractor_node(state: AgentState):
    return run_extractor(state["user_input"])

def mapper_node(state: AgentState):
    result = run_mapper(state["extracted_json"], state["user_input"])
    return {"mapped_json": result["mapped_json"]}

def query_node(state: AgentState):
    result = execute_deterministic_patient_search(state.get("mapped_json", state["extracted_json"]))
    return {"eligible_patients": str(result["eligible_patients"].to_dict())}

def auditor_node(state: AgentState):
    summary = (
        "✅ **Validation Complete.** \n\n"
        "Based on the protocol, the Data Engine successfully found eligible patients. \n\n"
        f"**Top Eligible Patient IDs:** {state['eligible_patients']}"
    )
    return {"final_output": summary}

def route_input(state: AgentState) -> str:
    return "continue" if state["is_valid"] == "VALID" else "block"


# ── Graph Assembly ─────────────────────────────────────────────────────────────
workflow = StateGraph(AgentState)
workflow.add_node("Gatekeeper", gatekeeper_node)
workflow.add_node("Error_Node", error_node)
workflow.add_node("Extractor", extractor_node)
workflow.add_node("Mapper", mapper_node)
workflow.add_node("Data_Query", query_node)
workflow.add_node("Auditor", auditor_node)

workflow.set_entry_point("Gatekeeper")
workflow.add_conditional_edges("Gatekeeper", route_input, {"continue": "Extractor", "block": "Error_Node"})
workflow.add_edge("Extractor", "Mapper")
workflow.add_edge("Mapper", "Data_Query")
workflow.add_edge("Data_Query", "Auditor")
workflow.add_edge("Error_Node", END)
workflow.add_edge("Auditor", END)

app_logic = workflow.compile()
