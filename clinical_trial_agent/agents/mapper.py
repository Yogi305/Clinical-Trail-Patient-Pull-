"""
agents/mapper.py
----------------
Agent 2: The Entity Resolver (Ontology Mapper & Re-Ranker)

Resolves raw LLM-extracted clinical text (e.g., "High BP") to the official
database keys (e.g., "Hypertension") using a FAISS vector similarity search
followed by an LLM re-ranking step.

If the re-ranker cannot confidently resolve a term, it marks it as
AMBIGUOUS_RAW:<original_text>, triggering the Human-in-the-Loop (HITL) UI.
"""

from langchain_core.prompts import ChatPromptTemplate
from agents.shared import (
    invoke_with_rate_limit,
    reasoning_llm,
    faiss_index,
    ontology_mapping,
    embedding_model,
    get_safe_document_context,
)


def run_mapper(extracted_json: dict, user_input: str) -> dict:
    """
    Maps extracted raw criteria to official schema terms using FAISS + LLM re-ranking.
    Returns {"mapped_json": {...}, "faiss_details": {...}}.
    """
    raw_criteria = extracted_json.copy()
    mapped_criteria = raw_criteria.copy()
    faiss_details = {}  # Stored for UI display of FAISS retrieval details

    fields_to_map = ["medical_condition", "admission_type", "blood_type", "medication", "test_results"]

    for field in fields_to_map:
        raw_val = raw_criteria.get(field)
        if not raw_val or str(raw_val).strip() == "" or str(raw_val).lower() in ("none",):
            continue

        # Step 1: Compute embedding and retrieve top-5 FAISS candidates
        vec = embedding_model.encode([str(raw_val)]).astype("float32")
        distances, indices = faiss_index.search(vec, 5)

        top_matches = [
            {
                "term": ontology_mapping[idx]["term"],
                "column": ontology_mapping[idx].get("column", ontology_mapping[idx].get("category", "Unknown")),
                "distance": float(distances[0][i]),
            }
            for i, idx in enumerate(indices[0])
            if idx != -1
        ]

        faiss_details[field] = {"raw_input": raw_val, "top_matches": top_matches}

        # Step 2: LLM re-ranks the top candidates and selects the best match
        rerank_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are an expert Clinical Data manager. "
             "The user extracted a messy clinical requirement: '{raw_val}' for the field '{field}'. "
             "You must select the PERFECT matching official database term from this exact list: {matches}. "
             "If the exact equivalent exists, reply with ONLY the exact text from the list. "
             "If there are multiple extremely ambiguous options or no safe medical match, reply with ONLY 'AMBIGUOUS'."),
            ("user", "Full Context of Protocol:\n{context}")
        ])

        match_terms = [m["term"] for m in top_matches]
        response = invoke_with_rate_limit(rerank_prompt | reasoning_llm, {
            "raw_val": raw_val,
            "field": field,
            "matches": str(match_terms),
            "context": get_safe_document_context(user_input)[:2500],
        })

        final_term = response.content.strip().replace('"', "").replace("'", "")

        if final_term == "AMBIGUOUS":
            mapped_criteria[field] = f"AMBIGUOUS_RAW:{raw_val}"
            faiss_details[field]["resolved_to"] = "⚠️ AMBIGUOUS"
        else:
            mapped_criteria[field] = final_term
            faiss_details[field]["resolved_to"] = final_term

    return {"mapped_json": mapped_criteria, "faiss_details": faiss_details}
