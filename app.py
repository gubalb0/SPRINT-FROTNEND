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
        '<div class="sidebar-logo">'
        '<span class="logo-forzy">forzy</span>'
        '<span class="logo-sub">uma empresa Promon</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # Badge de alertas críticos
    estados = st.session_state.get("estados_ativos", {})
    criticos = sum(1 for s in estados.values() if s == "critico")
    atencao = sum(1 for s in estados.values() if s == "atencao")

    if criticos:
        st.markdown(
            f'<div style="background:#DC3545;color:#fff;border-radius:8px;'
            f'padding:9px 14px;font-size:12px;font-weight:800;margin-bottom:6px;'
            f'text-align:center;letter-spacing:0.5px;">'
            f'🚨 {criticos} ATIVO(S) CRÍTICO(S)</div>',
            unsafe_allow_html=True,
        )
    if atencao:
        st.markdown(
            f'<div style="background:#FFC107;color:#4a3800;border-radius:8px;'
            f'padding:8px 14px;font-size:11.5px;font-weight:800;margin-bottom:8px;'
            f'text-align:center;">⚠️ {atencao} EM ATENÇÃO</div>',
            unsafe_allow_html=True,
        )

    pages = {
        "🚨  Painel de Alertas": "operations_panel",
        "🏠  Dashboard":         "dashboard",
        "🏭  Plantas & Áreas":   "plant_nav",
        "📊  Telemetria":        "telemetry",
        "📜  Histórico":         "alerts",
        "📋  Equipamentos":      "equipment_list",
        "➕  Cadastro":          "equipment_form",
        "🔢  Dados Brutos":      "raw_data",
    }

    if "active_page" not in st.session_state:
        st.session_state.active_page = "operations_panel"

    for label, key in pages.items():
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.active_page = key
            if key == "equipment_form":
                st.session_state.form_mode = "new"
                st.session_state.edit_data = None
            st.rerun()

    st.markdown("---")

    if st.button("♻️  Reiniciar Simulação", use_container_width=True, key="reset_sim"):
        for k in ("ciclo_analise", "estados_ativos", "eventos_novos",
                  "mudancas_estado", "historico_eventos", "ultima_analise"):
            st.session_state.pop(k, None)
        st.session_state.active_page = "operations_panel"
        st.rerun()

    st.markdown(
        '<p style="color:#888;font-size:11px;text-align:center;margin-top:8px;">'
        'Motor Intelligence v3.0<br>Sprint 3 — Inteligência Operacional</p>',
        unsafe_allow_html=True,
    )

# ── Page Router ─────────────────────────────────────────────────────────────
page = st.session_state.active_page

if page == "operations_panel":
    from pages import operations_panel; operations_panel.render()
elif page == "dashboard":
    from pages import dashboard; dashboard.render()
elif page == "plant_nav":
    from pages import plant_nav; plant_nav.render()
elif page == "telemetry":
    from pages import telemetry; telemetry.render()
elif page == "alerts":
    from pages import alerts; alerts.render()
elif page == "equipment_list":
    from pages import equipment_list; equipment_list.render()
elif page == "equipment_form":
    from pages import equipment_form; equipment_form.render()
elif page == "raw_data":
    from pages import raw_data; raw_data.render()
