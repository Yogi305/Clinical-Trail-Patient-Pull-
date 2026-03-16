"""
ui/sidebar.py
-------------
Renders the left sidebar containing cached S3 sample BRD download buttons.
"""

import streamlit as st
import requests


@st.cache_data(show_spinner=False)
def _fetch_brd_bytes(url: str):
    """Cache the raw bytes of each sample BRD so S3 is only hit once per session."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        st.error(f"Could not load sample from S3: {e}")
    return None


_SAMPLE_BRDS = [
    {"name": "BRD 1: Straightforward (Exact)",   "url": "https://clinicaldata-765366202501-ap-southeast-2-an.s3.ap-southeast-2.amazonaws.com/BRD+1.docx"},
    {"name": "BRD 2: Semantic (Language)",        "url": "https://clinicaldata-765366202501-ap-southeast-2-an.s3.ap-southeast-2.amazonaws.com/BRD+2.docx"},
    {"name": "BRD 3: HITL (Condition Ambiguity)", "url": "https://clinicaldata-765366202501-ap-southeast-2-an.s3.ap-southeast-2.amazonaws.com/BRD+3.docx"},
    {"name": "BRD 4: HITL (Medication Ambiguity)","url": "https://clinicaldata-765366202501-ap-southeast-2-an.s3.ap-southeast-2.amazonaws.com/BRD+4.docx"},
]


def render_sidebar():
    with st.sidebar:
        st.header("📂 Sample Protocols")
        st.markdown("Download these sample BRDs to test the agent workflow.")

        for sample in _SAMPLE_BRDS:
            content = _fetch_brd_bytes(sample["url"])
            if content:
                file_name = sample["url"].split("/")[-1].replace("+", " ")
                st.download_button(
                    label=f"📥 {sample['name']}",
                    data=content,
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )

        st.divider()
        st.info("💡 **Tip:** After downloading, upload the file in the 'Agent Interface' tab to see the agentic magic.")
