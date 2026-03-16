"""
agents/gatekeeper.py
--------------------
Agent 0: The Gatekeeper (Semantic Router / Red-Team Defense)

Validates that the incoming user input is a genuine clinical trial protocol.
Instantly blocks off-topic questions, prompt injections, and irrelevant text
before they consume any downstream compute resources.
"""

from langchain_core.prompts import ChatPromptTemplate
from agents.shared import invoke_with_rate_limit, router_llm


def run_gatekeeper(user_input: str) -> dict:
    """
    Returns {"is_valid": "VALID"} or {"is_valid": "INVALID"}.
    Uses the fast 8b router model to keep cost and latency minimal.
    """
    short_input = str(user_input)[:2000]  # Guard: never pass huge documents to the gatekeeper

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a strict security guard for a clinical trial system. "
         "If the user input is a clinical trial protocol, BRD, or medical criteria, reply with ONLY 'VALID'. "
         "If it is a general question, coding request, or asking about a specific named person, reply with ONLY 'INVALID'."),
        ("user", "{input}")
    ])

    response = invoke_with_rate_limit(prompt | router_llm, {"input": short_input})
    is_valid = response.content.strip().upper()
    return {"is_valid": is_valid}
