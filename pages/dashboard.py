import streamlit as st


def render():
    eq_list = st.session_state.get("equipment_list", [])
    total = len(eq_list)
    ativos = sum(1 for e in eq_list if e["status"] == "Ativo")
    manut  = sum(1 for e in eq_list if e["status"] == "Manutenção")
    inat   = sum(1 for e in eq_list if e["status"] == "Inativo")

    # ── Topbar accent ──────────────────────────────────────────
    st.markdown(
        '<div class="topbar-strip">'
        '<div class="strip-seg s1"></div>'
        '<div class="strip-seg s2"></div>'
        '<div class="strip-seg s3"></div>'
        '<div class="strip-seg s4"></div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="page-header">'
        "<h1>Dashboard</h1>"
        "<p>Visão geral do parque de equipamentos monitorados</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    # ── KPI Cards ──────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown(
            f'<div class="kpi-card">'
            f'<div class="kpi-icon">⚙️</div>'
            f'<div class="kpi-value">{total}</div>'
            f'<div class="kpi-label">Total de Equipamentos</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    with k2:
        st.markdown(
            f'<div class="kpi-card success">'
            f'<div class="kpi-icon">✅</div>'
            f'<div class="kpi-value">{ativos}</div>'
            f'<div class="kpi-label">Ativos / Operando</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    with k3:
        st.markdown(
            f'<div class="kpi-card yellow">'
            f'<div class="kpi-icon">🔧</div>'
            f'<div class="kpi-value">{manut}</div>'
            f'<div class="kpi-label">Em Manutenção</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    with k4:
        st.markdown(
            f'<div class="kpi-card purple">'
            f'<div class="kpi-icon">⛔</div>'
            f'<div class="kpi-value">{inat}</div>'
            f'<div class="kpi-label">Inativos</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Two-column layout ──────────────────────────────────────
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown('<div class="forzy-card"><h3>🏭 Equipamentos Recentes</h3>', unsafe_allow_html=True)

        if not eq_list:
            st.info("Nenhum equipamento cadastrado ainda.")
        else:
            rows_html = ""
            for eq in eq_list[-5:][::-1]:
                badge_cls = {
                    "Ativo": "status-active",
                    "Manutenção": "status-maint",
                    "Inativo": "status-inactive",
                }.get(eq["status"], "status-inactive")
                rows_html += (
                    f"<tr>"
                    f'<td><span class="tag-badge">{eq["tag"]}</span></td>'
                    f"<td>{eq['nome']}</td>"
                    f"<td>{eq['fabricante']}</td>"
                    f"<td>{eq['potencia_kw']} kW</td>"
                    f'<td><span class="status-badge {badge_cls}">{eq["status"]}</span></td>'
                    f"</tr>"
                )

            st.markdown(
                f"""
                <table class="forzy-table">
                  <thead>
                    <tr>
                      <th>TAG</th><th>Nome</th><th>Fabricante</th>
                      <th>Potência</th><th>Status</th>
                    </tr>
                  </thead>
                  <tbody>{rows_html}</tbody>
                </table>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="forzy-card"><h3>🔢 Estatísticas</h3>', unsafe_allow_html=True)

        total_kw = sum(e["potencia_kw"] for e in eq_list)
        fabricantes = list({e["fabricante"] for e in eq_list})

        st.metric("Potência Total Instalada", f"{total_kw:.1f} kW")
        st.metric("Fabricantes Distintos", len(fabricantes))
        st.metric("Disponibilidade", f"{(ativos/total*100):.0f}%" if total else "—")

        st.markdown("<br>", unsafe_allow_html=True)

        if fabricantes:
            st.markdown(
                '<div class="section-divider"><span>Fabricantes</span></div>',
                unsafe_allow_html=True,
            )
            fab_count = {}
            for e in eq_list:
                fab_count[e["fabricante"]] = fab_count.get(e["fabricante"], 0) + 1
            for fab, cnt in fab_count.items():
                pct = cnt / total * 100
                st.markdown(
                    f"""
                    <div style="margin-bottom:10px;">
                      <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px;">
                        <span style="font-weight:600">{fab}</span>
                        <span style="color:#888">{cnt} equip.</span>
                      </div>
                      <div style="background:#eee;border-radius:4px;height:6px;">
                        <div style="background:#FF6B00;border-radius:4px;height:6px;width:{pct:.0f}%"></div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Quick action buttons ───────────────────────────────────
    st.markdown('<div class="section-divider"><span>Ações Rápidas</span></div>', unsafe_allow_html=True)

    qa1, qa2, qa3 = st.columns(3)
    with qa1:
        if st.button("➕  Cadastrar Novo Equipamento", use_container_width=True):
            st.session_state.form_mode = "new"
            st.session_state.edit_data = None
            st.session_state.active_page = "equipment_form"
            st.rerun()
    with qa2:
        if st.button("📋  Ver Lista Completa", use_container_width=True):
            st.session_state.active_page = "equipment_list"
            st.rerun()
    with qa3:
        if st.button("📊  Visualizar Dados Brutos", use_container_width=True):
            st.session_state.active_page = "raw_data"
            st.rerun()
