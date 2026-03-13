import os
import json
import pandas as pd
from typing import TypedDict, Dict, Any, Literal
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import time
from tenacity import retry, wait_exponential, stop_after_attempt
from pydantic import BaseModel, Field
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer

load_dotenv()

# 1. Define the LangGraph State
class AgentState(TypedDict):
    user_input: str
    is_valid: str
    extracted_json: Dict[str, Any]
    mapped_json: Dict[str, Any]
    eligible_patients: str
    final_output: str

# Initialize Specialized LLMs for Multi-Agent routing
# 1.4 Initialize Models
router_llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0) # Blazing fast, cheap for routing
reasoning_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0) # High param reasoning for extraction

# 1.5 Define Pydantic Schema for Strict Extraction
class ClinicalCriteria(BaseModel):
    age_min: int = Field(default=None, description="Minimum age requirement for the patient")
    age_max: int = Field(default=None, description="Maximum age requirement for the patient")
    gender: str = Field(default=None, description="Gender requirement, e.g., Male, Female")
    medical_condition: str = Field(default=None, description="Required medical condition or diagnosis")
    admission_type: str = Field(default=None, description="Required admission type, e.g., Urgent, Elective, Emergency")
    blood_type: str = Field(default=None, description="Blood type requirement")
    medication: str = Field(default=None, description="Required or exclusionary medication")
    test_results: str = Field(default=None, description="Required test results status, e.g., Normal, Abnormal")
    # Exclusion Criteria
    exclude_medication: str = Field(default=None, description="Medication that DISQUALIFIES a patient, e.g., Lipitor")
    exclude_test_results: str = Field(default=None, description="Test results that DISQUALIFY a patient, e.g., Normal")
    exclude_admission_type: str = Field(default=None, description="Admission type that DISQUALIFIES a patient, e.g., Emergency")

# Load the structured dataset
db_path = "https://clinicaldata-765366202501-ap-southeast-2-an.s3.ap-southeast-2.amazonaws.com/healthcare_dataset.csv"
df = pd.read_csv(db_path)

# Load FAISS Ontology DB
index_path = os.path.join(os.path.dirname(__file__), "ontology.index")
mapping_path = os.path.join(os.path.dirname(__file__), "ontology_mapping.pkl")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
faiss_index = faiss.read_index(index_path)
with open(mapping_path, "rb") as f:
    ontology_mapping = pickle.load(f)

# Rate Limiting Decorator for FREE API Tiers
# Groq free tier has strict TPM limits — sequential agent calls can exhaust the budget.
# We use aggressive backoff to wait for the quota to reset between calls.
@retry(wait=wait_exponential(multiplier=2, min=5, max=30), stop=stop_after_attempt(5))
def invoke_with_rate_limit(chain, inputs):
    time.sleep(5) # Prevent rapid burst limit — give Groq's TPM window time to reset
    return chain.invoke(inputs)

# Safety net: Truncate extremely large documents to stay within Groq Free Tier TPM limits
# For our realistic BRDs (~500-800 words), the full text is always passed through.
def get_safe_document_context(text: str, max_words: int = 3000) -> str:
    words = text.split()
    if len(words) > max_words:
        return " ".join(words[:max_words])
    return text

# =====================================================================
# STANDALONE NODE FUNCTIONS (Callable individually from Streamlit UI)
# =====================================================================

# NODE 0: The Gatekeeper (Semantic Router / Red-Team Defense)
def run_gatekeeper(user_input: str) -> dict:
    short_input = str(user_input)[:2000]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a strict security guard for a clinical trial system. "
                   "If the user input is a clinical trial protocol, BRD, or medical criteria, reply with ONLY 'VALID'. "
                   "If it is a general question, coding request, or asking about a specific named person, reply with ONLY 'INVALID'."),
        ("user", "{input}")
    ])
    response = invoke_with_rate_limit(prompt | router_llm, {"input": short_input})
    is_valid = response.content.strip().upper()
    return {"is_valid": is_valid}

# NODE 1: The Protocol Analyst (Reasoning Engine with Pydantic)
def run_extractor(user_input: str) -> dict:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert clinical trial protocol analyst. Your ONLY job is to extract PATIENT ELIGIBILITY criteria. "
                   "SCOPE RESTRICTION: Only extract criteria that directly describe WHICH PATIENTS qualify or disqualify for the trial. "
                   "This includes: age requirements, gender, medical conditions, medications, test results, blood types, and admission types. "
                   "DO NOT extract: regulatory requirements (ICH-GCP, FDA rules), operational logistics (cold-chain, data encryption), "
                   "investigator qualifications, study design methodology, pharmacovigilance rules, or any other non-patient criteria. "
                   "INCLUSION fields: Fill the standard fields (age_min, age_max, gender, medical_condition, etc.) with criteria patients MUST meet. "
                   "EXCLUSION fields: Fill the 'exclude_' prefixed fields with criteria that DISQUALIFY a patient from the trial. "
                   "For example: 'Patients on Lipitor are excluded' → exclude_medication='Lipitor'. "
                   "'Test Results of Normal are rejected' → exclude_test_results='Normal'. "
                   "If a field is not explicitly mentioned as a patient requirement, leave it null/empty. Do not guess. "
                   "Return ONLY the structured output."),
        ("user", "{input}")
    ])
    
    # Pass the text to Groq 70b with structured output
    structured_llm = reasoning_llm.with_structured_output(ClinicalCriteria)
    safe_input = get_safe_document_context(user_input)
    response = invoke_with_rate_limit(prompt | structured_llm, {"input": safe_input})
    return {"extracted_json": response.dict()}

# NODE 2: The Entity Resolver (Ontology Mapper & Re-ranker)
def run_mapper(extracted_json: dict, user_input: str) -> dict:
    raw_criteria = extracted_json.copy()
    mapped_criteria = raw_criteria.copy()
    faiss_details = {}  # Store the FAISS retrieval details for UI display
    
    fields_to_map = ['medical_condition', 'admission_type', 'blood_type', 'medication', 'test_results']
    
    for field in fields_to_map:
        raw_val = raw_criteria.get(field)
        if raw_val and str(raw_val).strip() != "" and str(raw_val).lower() not in ('none',):
            vec = embedding_model.encode([str(raw_val)]).astype('float32')
            
            k = 5
            distances, indices = faiss_index.search(vec, k)
            
            top_matches = []
            for i, idx in enumerate(indices[0]):
                if idx != -1:
                    match_data = ontology_mapping[idx]
                    top_matches.append({
                        "term": match_data['term'],
                        "column": match_data.get('column', match_data.get('category', 'Unknown')),
                        "distance": float(distances[0][i])
                    })
            
            faiss_details[field] = {
                "raw_input": raw_val,
                "top_matches": top_matches
            }
                    
            rerank_prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert Clinical Data manager. "
                           "The user extracted a messy clinical requirement: '{raw_val}' for the field '{field}'. "
                           "You must select the PERFECT matching official database term from this exact list: {matches}. "
                           "If the exact equivalent exists, reply with ONLY the exact text from the list. "
                           "If there are multiple extremely ambiguous options or no safe medical match, reply with ONLY 'AMBIGUOUS'."),
                ("user", "Full Context of Protocol:\n{context}")
            ])
            
            match_terms = [m['term'] for m in top_matches]
            # Use Groq for the re-ranking reasoning (it's a short input)
            response = invoke_with_rate_limit(rerank_prompt | reasoning_llm, {
                "raw_val": raw_val,
                "field": field,
                "matches": str(match_terms),
                "context": get_safe_document_context(user_input)[:2500]
            })
            
            final_term = response.content.strip().replace('"', '').replace("'", "")
            
            if final_term == "AMBIGUOUS":
                mapped_criteria[field] = f"AMBIGUOUS_RAW:{raw_val}"
                faiss_details[field]["resolved_to"] = "⚠️ AMBIGUOUS"
            else:
                mapped_criteria[field] = final_term
                faiss_details[field]["resolved_to"] = final_term
                
    return {"mapped_json": mapped_criteria, "faiss_details": faiss_details}

# NODE 3: Deterministic Data Engine
def run_query(mapped_json: dict) -> dict:
    criteria = mapped_json
    filtered_df = df.copy()
    filter_log = []
    
    def is_valid_schema(val):
        return val and str(val).lower() not in ('none', 'n/a', 'any', 'null') and not str(val).startswith("AMBIGUOUS_RAW:")
    
    filter_log.append(f"🟢 Starting with **{len(filtered_df)}** patient records.")
    
    if "medical_condition" in criteria and is_valid_schema(criteria["medical_condition"]):
        filtered_df = filtered_df[filtered_df['Medical Condition'] == str(criteria['medical_condition'])]
        filter_log.append(f"After `Medical Condition == '{criteria['medical_condition']}'`: **{len(filtered_df)}** patients remain.")
        
    if "age_min" in criteria and criteria["age_min"]:
        filtered_df = filtered_df[filtered_df['Age'] >= int(criteria['age_min'])]
        filter_log.append(f"After `Age >= {criteria['age_min']}`: **{len(filtered_df)}** patients remain.")
        
    if "age_max" in criteria and criteria["age_max"]:
        filtered_df = filtered_df[filtered_df['Age'] <= int(criteria['age_max'])]
        filter_log.append(f"After `Age <= {criteria['age_max']}`: **{len(filtered_df)}** patients remain.")
        
    if "gender" in criteria and is_valid_schema(criteria["gender"]):
        gender_cond = str(criteria['gender']).title()
        filtered_df = filtered_df[filtered_df['Gender'] == gender_cond]
        filter_log.append(f"After `Gender == '{gender_cond}'`: **{len(filtered_df)}** patients remain.")

    if "admission_type" in criteria and is_valid_schema(criteria["admission_type"]):
        filtered_df = filtered_df[filtered_df['Admission Type'] == str(criteria['admission_type'])]
        filter_log.append(f"After `Admission Type == '{criteria['admission_type']}'`: **{len(filtered_df)}** patients remain.")
    
    if "blood_type" in criteria and is_valid_schema(criteria["blood_type"]):
        filtered_df = filtered_df[filtered_df['Blood Type'] == str(criteria['blood_type']).upper()]
        filter_log.append(f"After `Blood Type == '{criteria['blood_type']}'`: **{len(filtered_df)}** patients remain.")
    
    if "medication" in criteria and is_valid_schema(criteria["medication"]):
        filtered_df = filtered_df[filtered_df['Medication'] == str(criteria['medication'])]
        filter_log.append(f"After `Medication == '{criteria['medication']}'`: **{len(filtered_df)}** patients remain.")
    
    if "test_results" in criteria and is_valid_schema(criteria["test_results"]):
        filtered_df = filtered_df[filtered_df['Test Results'] == str(criteria['test_results'])]
        filter_log.append(f"After `Test Results == '{criteria['test_results']}'`: **{len(filtered_df)}** patients remain.")
    
    # --- EXCLUSION FILTERS (NOT EQUAL) ---
    filter_log.append("🔴 **Applying Exclusion Criteria...**")
    
    if "exclude_medication" in criteria and is_valid_schema(criteria["exclude_medication"]):
        filtered_df = filtered_df[filtered_df['Medication'] != str(criteria['exclude_medication'])]
        filter_log.append(f"After `Medication != '{criteria['exclude_medication']}'` (EXCLUDED): **{len(filtered_df)}** patients remain.")
    
    if "exclude_test_results" in criteria and is_valid_schema(criteria["exclude_test_results"]):
        filtered_df = filtered_df[filtered_df['Test Results'] != str(criteria['exclude_test_results'])]
        filter_log.append(f"After `Test Results != '{criteria['exclude_test_results']}'` (EXCLUDED): **{len(filtered_df)}** patients remain.")

    if "exclude_admission_type" in criteria and is_valid_schema(criteria["exclude_admission_type"]):
        filtered_df = filtered_df[filtered_df['Admission Type'] != str(criteria['exclude_admission_type'])]
        filter_log.append(f"After `Admission Type != '{criteria['exclude_admission_type']}'` (EXCLUDED): **{len(filtered_df)}** patients remain.")
    
    filter_log.append(f"🏁 **Final Result: {len(filtered_df)} eligible patients found.**")
    
    return {
        "eligible_patients": filtered_df,
        "filter_log": filter_log,
        "total_matched": len(filtered_df)
    }

# =====================================================================
# LANGGRAPH DEFINITION (Kept for Architecture Diagram / Reference)
# =====================================================================
def gatekeeper_node(state: AgentState):
    result = run_gatekeeper(state["user_input"])
    return result

def error_node(state: AgentState):
    return {"final_output": "🛡️ **Guardrail Triggered:** I am a specialized Clinical Trial AI. I can only process Clinical Trial Protocols and Business Requirement Documents. Request blocked."}

def extractor_node(state: AgentState):
    result = run_extractor(state["user_input"])
    return result

def mapper_node(state: AgentState):
    result = run_mapper(state["extracted_json"], state["user_input"])
    return {"mapped_json": result["mapped_json"]}

def query_node(state: AgentState):
    result = run_query(state.get("mapped_json", state["extracted_json"]))
    return {"eligible_patients": str(result["eligible_patients"].to_dict())}

def auditor_node(state: AgentState):
    summary = f"✅ **Validation Complete.** \n\nBased on the protocol, the Data Engine successfully found eligible patients. \n\n**Top Eligible Patient IDs:** {state['eligible_patients']}"
    return {"final_output": summary}

def route_input(state: AgentState):
    return "continue" if state["is_valid"] == "VALID" else "block"

# --- Build the StateGraph (for reference / visualization) ---
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
