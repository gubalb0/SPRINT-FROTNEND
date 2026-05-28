import streamlit as st
from datetime import datetime


def render():
    eq_list = st.session_state.get("equipment_list", [])
    alertas = st.session_state.get("alertas", [])
    total   = len(eq_list)
    ativos  = sum(1 for e in eq_list if e["status"] == "Ativo")
    manut   = sum(1 for e in eq_list if e["status"] == "Manutenção")
    inat    = sum(1 for e in eq_list if e["status"] == "Inativo")
    criticos = sum(1 for e in eq_list if e.get("saude") == "critico")

    st.markdown(
        '<div class="topbar-strip">'
        '<div class="strip-seg s1"></div><div class="strip-seg s2"></div>'
        '<div class="strip-seg s3"></div><div class="strip-seg s4"></div>'
        '</div>', unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="page-header"><h1>Dashboard</h1>'
        '<p>Visão geral do parque de equipamentos monitorados</p></div>',
        unsafe_allow_html=True,
    )

    # ── KPI Cards ──────────────────────────────────────────────
    k1, k2, k3, k4, k5 = st.columns(5)
    kpis = [
        (k1, total,    "Total de Equipamentos",  "⚙️",  "",        "#FF6B00"),
        (k2, ativos,   "Ativos / Operando",       "✅",  "success", "#28A745"),
        (k3, manut,    "Em Manutenção",            "🔧",  "yellow",  "#C89A00"),
        (k4, inat,     "Inativos",                 "⛔",  "purple",  "#3D1A6E"),
        (k5, criticos, "Alertas Críticos",         "🚨",  "",        "#DC3545"),
    ]
    for col, val, label, icon, cls, cor in kpis:
        with col:
            border = f"border-top-color:{cor};" if not cls else ""
            st.markdown(
                f'<div class="kpi-card {cls}" style="{border}">'
                f'<div class="kpi-icon">{icon}</div>'
                f'<div class="kpi-value" style="color:{cor};">{val}</div>'
                f'<div class="kpi-label">{label}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Alertas ativos no topo ─────────────────────────────────
    alertas_crit = [a for a in alertas if a["tipo"] == "critico"]
    if alertas_crit:
        for a in alertas_crit:
            st.markdown(
                f"""
                <div style="background:#fff0f0;border-radius:8px;padding:12px 18px;
                            border-left:5px solid #DC3545;margin-bottom:8px;color:#111;
                            display:flex;justify-content:space-between;align-items:center;">
                  <span>🔴 <strong>{a['tag']}</strong> — {a['mensagem']}</span>
                  <span style="font-size:11px;color:#888;">🕐 {a['timestamp']}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown('<div class="forzy-card"><h3>🏭 Equipamentos Recentes</h3>', unsafe_allow_html=True)
        if not eq_list:
            st.info("Nenhum equipamento cadastrado ainda.")
        else:
            rows_html = ""
            for eq in eq_list[-5:][::-1]:
                saude   = eq.get("saude", "normal")
                badge_s = {"normal": "status-active", "atencao": "status-maint", "critico": "status-inactive"}.get(saude, "")
                icon_s  = {"normal": "🟢", "atencao": "🟡", "critico": "🔴"}.get(saude, "")
                badge_e = {"Ativo": "status-active", "Manutenção": "status-maint", "Inativo": "status-inactive"}.get(eq["status"], "")
                rows_html += (
                    f"<tr>"
                    f'<td><span class="tag-badge">{eq["tag"]}</span></td>'
                    f"<td>{eq['nome']}</td>"
                    f"<td>{eq['fabricante']}</td>"
                    f"<td style='color:#FF6B00;font-weight:700'>{eq['potencia_kw']} kW</td>"
                    f'<td><span class="status-badge {badge_e}">{eq["status"]}</span></td>'
                    f'<td>{icon_s}</td>'
                    f"</tr>"
                )
            st.markdown(
                f"""<table class="forzy-table">
                  <thead><tr><th>TAG</th><th>Nome</th><th>Fabricante</th>
                  <th>Potência</th><th>Status</th><th>Saúde</th></tr></thead>
                  <tbody>{rows_html}</tbody></table>""",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="forzy-card"><h3>🔢 Estatísticas</h3>', unsafe_allow_html=True)
        total_kw    = sum(e["potencia_kw"] for e in eq_list)
        fabricantes = list({e["fabricante"] for e in eq_list})
        st.metric("Potência Total Instalada", f"{total_kw:.1f} kW")
        st.metric("Fabricantes Distintos", len(fabricantes))
        st.metric("Disponibilidade", f"{(ativos/total*100):.0f}%" if total else "—")

        if fabricantes:
            st.markdown('<div class="section-divider"><span>Fabricantes</span></div>', unsafe_allow_html=True)
            fab_count = {}
            for e in eq_list:
                fab_count[e["fabricante"]] = fab_count.get(e["fabricante"], 0) + 1
            for fab, cnt in fab_count.items():
                pct = cnt / total * 100
                st.markdown(
                    f"""<div style="margin-bottom:10px;">
                      <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px;">
                        <span style="font-weight:600;color:#111">{fab}</span>
                        <span style="color:#888">{cnt} equip.</span>
                      </div>
                      <div style="background:#eee;border-radius:4px;height:6px;">
                        <div style="background:#FF6B00;border-radius:4px;height:6px;width:{pct:.0f}%"></div>
                      </div></div>""",
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Quick actions ──────────────────────────────────────────
    st.markdown('<div class="section-divider"><span>Ações Rápidas</span></div>', unsafe_allow_html=True)
    qa1, qa2, qa3, qa4, qa5 = st.columns(5)
    actions = [
        (qa1, "➕ Cadastrar",    "equipment_form", "new"),
        (qa2, "📋 Equipamentos", "equipment_list", None),
        (qa3, "🏭 Plantas",      "plant_nav",      None),
        (qa4, "📊 Telemetria",   "telemetry",      None),
        (qa5, "🚨 Alertas",      "alerts",         None),
    ]
    for col, label, page, mode in actions:
        with col:
            if st.button(label, use_container_width=True, key=f"qa_{page}"):
                st.session_state.active_page = page
                if mode:
                    st.session_state.form_mode = mode
                    st.session_state.edit_data = None
                st.rerun()
