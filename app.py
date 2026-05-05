import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from utils.session import init_session
from utils.theme import inject_css

st.set_page_config(
    page_title="Forzy — Motor Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
init_session()

# ── Sidebar / Menu ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-logo">
            <span class="logo-forzy">forzy</span>
            <span class="logo-sub">uma empresa Promon</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    pages = {
        "🏠  Dashboard": "dashboard",
        "📋  Equipamentos": "equipment_list",
        "➕  Cadastro": "equipment_form",
        "📊  Dados Brutos": "raw_data",
    }

    if "active_page" not in st.session_state:
        st.session_state.active_page = "dashboard"

    for label, key in pages.items():
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.active_page = key
            st.rerun()

    st.markdown("---")
    st.markdown(
        '<p style="color:#888;font-size:11px;text-align:center;">Motor Intelligence v1.0<br>Sprint 1 — Cadastro Técnico</p>',
        unsafe_allow_html=True,
    )

# ── Page Router ─────────────────────────────────────────────────────────────
page = st.session_state.active_page

if page == "dashboard":
    from pages import dashboard
    dashboard.render()
elif page == "equipment_list":
    from pages import equipment_list
    equipment_list.render()
elif page == "equipment_form":
    from pages import equipment_form
    equipment_form.render()
elif page == "raw_data":
    from pages import raw_data
    raw_data.render()
