"""
agents/extractor.py
-------------------
Agent 1: The Protocol Analyst (Reasoning Engine with Pydantic)

Reads verbose, unstructured clinical trial BRD text and extracts a perfectly
structured JSON payload of patient eligibility criteria (inclusion + exclusion).
Uses Pydantic schema enforcement via LangChain's with_structured_output().
"""

from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from agents.shared import invoke_with_rate_limit, reasoning_llm, get_safe_document_context


# ── Pydantic Schema for Strict Extraction ─────────────────────────────────────
class ClinicalCriteria(BaseModel):
    """Structured patient eligibility criteria extracted from a clinical trial BRD."""
    age_min: Optional[int] = Field(default=None, description="Minimum age requirement for the patient")
    age_max: Optional[int] = Field(default=None, description="Maximum age requirement for the patient")
    gender: Optional[str] = Field(default=None, description="Gender requirement, e.g., Male, Female")
    medical_condition: Optional[str] = Field(default=None, description="Required medical condition or diagnosis")
    admission_type: Optional[str] = Field(default=None, description="Required admission type, e.g., Urgent, Elective, Emergency")
    blood_type: Optional[str] = Field(default=None, description="Blood type requirement")
    medication: Optional[str] = Field(default=None, description="Required or exclusionary medication")
    test_results: Optional[str] = Field(default=None, description="Required test results status, e.g., Normal, Abnormal")
    # Exclusion Criteria
    exclude_medication: Optional[str] = Field(default=None, description="Medication that DISQUALIFIES a patient, e.g., Lipitor")
    exclude_test_results: Optional[str] = Field(default=None, description="Test results that DISQUALIFY a patient, e.g., Normal")
    exclude_admission_type: Optional[str] = Field(default=None, description="Admission type that DISQUALIFIES a patient, e.g., Emergency")


def run_extractor(user_input: str) -> dict:
    """
    Calls Groq LLaMA-70b with Pydantic-enforced structured output to extract
    patient eligibility criteria from the raw protocol document text.
    Returns {"extracted_json": {...}} or an empty schema on failure.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an expert clinical trial protocol analyst. Your ONLY job is to extract PATIENT ELIGIBILITY criteria. "
         "SCOPE RESTRICTION: Only extract criteria that directly describe WHICH PATIENTS qualify or disqualify for the trial. "
         "This includes: age requirements, gender, medical conditions, medications, test results, blood types, and admission types. "
         "DO NOT extract: regulatory requirements (ICH-GCP, FDA rules), operational logistics (cold-chain, data encryption), "
         "investigator qualifications, study design methodology, pharmacovigilance rules, or any other non-patient criteria. "
         "INCLUSION fields: Fill the standard fields (age_min, age_max, gender, medical_condition, etc.) with criteria patients MUST meet. "
         "EXCLUSION fields: Fill the 'exclude_' prefixed fields with criteria that DISQUALIFY a patient from the trial. "
         "For example: 'Patients on Lipitor are excluded' → exclude_medication='Lipitor'. "
         "If a field is not explicitly mentioned as a patient requirement, leave it null/empty. Do not guess. "
         "Return ONLY the structured output."),
        ("user", "{input}")
    ])

    try:
        structured_llm = reasoning_llm.with_structured_output(ClinicalCriteria)
        safe_input = get_safe_document_context(user_input)
        response = invoke_with_rate_limit(prompt | structured_llm, {"input": safe_input})
        return {"extracted_json": response.dict()}
    except Exception as e:
        import traceback
        print(f"\n[ERROR] Extraction Exception Details:")
        print(f"Type: {type(e)}")
        print(f"Message: {str(e)}")
        if hasattr(e, 'body'):
            print(f"Body: {e.body}")
        traceback.print_exc()
        # Graceful degradation: return empty valid schema so the pipeline doesn't crash
        return {"extracted_json": ClinicalCriteria().dict()}
