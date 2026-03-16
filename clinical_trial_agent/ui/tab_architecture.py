"""
ui/tab_architecture.py
----------------------
Renders Tab 3: Architecture Workflow.

Loads architecture.md, replaces the Mermaid code block with the
pre-generated architecture_diagram.png, and renders the surrounding text.
"""

import os
import re
import streamlit as st


def render_tab_architecture():
    try:
        base_dir = os.path.dirname(os.path.dirname(__file__))  # clinical_trial_agent root
        journey_path = os.path.join(base_dir, "architecture.md")

        if not os.path.exists(journey_path):
            st.error("Architecture markdown file not found.")
            return

        with open(journey_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Split around the mermaid code block so we can inject the image in its place
        parts = re.split(r"```mermaid\n.*?```", content, flags=re.DOTALL)

        st.markdown(parts[0])

        img_path = os.path.join(base_dir, "architecture_diagram.png")
        if os.path.exists(img_path):
            col1, col2, col3 = st.columns([1, 4, 1])
            with col2:
                st.image(img_path, use_column_width=True)

        if len(parts) > 1:
            st.markdown(parts[1])

    except Exception as e:
        st.error(f"Could not load architecture view: {e}")
