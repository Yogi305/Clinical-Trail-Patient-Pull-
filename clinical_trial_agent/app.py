"""
app.py — Entry Point
====================
Thin shell that assembles the Streamlit app from modular ui/ components.
Run with: streamlit run app.py
"""

import streamlit as st
from ui.sidebar import render_sidebar
from ui.tab_agent_interface import render_tab_agent_interface
from ui.tab_data_overview import render_tab_data_overview
from ui.tab_architecture import render_tab_architecture
from ui.tab_notebook_view import render_tab_notebook_view

st.set_page_config(page_title="Agilisium PoC: Clinical Trial Agent", layout="wide")
st.title("🧬 AI Clinical Trial Patient Matcher")

render_sidebar()

tab1, tab2, tab3, tab4 = st.tabs(["✨ Agent Interface", "📊 Data Overview (Phase 0)", "🏛️ Architecture Workflow", "🧬 Cleaning Workflow"])
with tab1:
    render_tab_agent_interface()
with tab2:
    render_tab_data_overview()
with tab3:
    render_tab_architecture()
with tab4:
    render_tab_notebook_view()
