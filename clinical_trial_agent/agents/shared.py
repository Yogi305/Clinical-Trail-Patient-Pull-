"""
agents/shared.py
----------------
Shared startup resources used by all agent modules:
  - Environment loading
  - LLM client initialization (Groq)
  - Patient DataFrame loading from S3
  - FAISS index + ontology mapping loading
  - Rate-limit retry decorator
  - Document context safety helper
"""

import os
import time
import pickle
import pandas as pd
import numpy as np
import faiss
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from sentence_transformers import SentenceTransformer
from tenacity import retry, wait_exponential, stop_after_attempt

load_dotenv()

# ── LLM Clients ───────────────────────────────────────────────────────────────
# Fast, cheap model for routing/gatekeeper
router_llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

# Powerful model for structured extraction and re-ranking
reasoning_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# ── Patient Database ───────────────────────────────────────────────────────────
DB_PATH = "https://clinicaldata-765366202501-ap-southeast-2-an.s3.ap-southeast-2.amazonaws.com/healthcare_dataset.csv"
patient_df = pd.read_csv(DB_PATH)

# ── FAISS Ontology Vector Database ────────────────────────────────────────────
_base_dir = os.path.dirname(os.path.dirname(__file__))  # clinical_trial_agent root
faiss_index = faiss.read_index(os.path.join(_base_dir, "ontology.index"))
with open(os.path.join(_base_dir, "ontology_mapping.pkl"), "rb") as f:
    ontology_mapping = pickle.load(f)

# Sentence embedding model — used by the Ontology Mapper for vector similarity
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# ── Rate-Limit Retry Decorator ─────────────────────────────────────────────────
# Groq free tier has strict TPM limits. This backs off gracefully instead of crashing.
@retry(wait=wait_exponential(multiplier=2, min=5, max=30), stop=stop_after_attempt(5))
def invoke_with_rate_limit(chain, inputs):
    time.sleep(5)  # Brief pause to prevent rapid-burst quota exhaustion
    return chain.invoke(inputs)


# ── Safety Context Truncation ──────────────────────────────────────────────────
def get_safe_document_context(text: str, max_words: int = 3000) -> str:
    """Truncate very large documents to stay within Groq's free-tier token limits."""
    words = text.split()
    if len(words) > max_words:
        return " ".join(words[:max_words])
    return text
