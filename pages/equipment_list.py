import streamlit as st


def render():
    st.markdown(
        '<div class="topbar-strip">'
        '<div class="strip-seg s2"></div><div class="strip-seg s1"></div>'
        '<div class="strip-seg s3"></div><div class="strip-seg s1"></div>'
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="page-header">'
        "<h1>Equipamentos Cadastrados</h1>"
        "<p>Clique em um equipamento para ver sua ficha técnica completa</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    eq_list = st.session_state.get("equipment_list", [])

    # ── Filtros ────────────────────────────────────────────────
    with st.expander("🔍  Filtros", expanded=False):
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            search = st.text_input("Buscar por nome / TAG", placeholder="ex: MTR-001")
        with fc2:
            fab_opts = ["Todos"] + sorted({e["fabricante"] for e in eq_list})
            fab_filter = st.selectbox("Fabricante", fab_opts)
        with fc3:
            status_opts = ["Todos", "Ativo", "Manutenção", "Inativo"]
            status_filter = st.selectbox("Status", status_opts)

    filtered = eq_list
    if search:
        search_l = search.lower()
        filtered = [e for e in filtered if search_l in e["nome"].lower() or search_l in e["tag"].lower()]
    if fab_filter != "Todos":
        filtered = [e for e in filtered if e["fabricante"] == fab_filter]
    if status_filter != "Todos":
        filtered = [e for e in filtered if e["status"] == status_filter]

    st.markdown(f"**{len(filtered)}** equipamento(s) encontrado(s)")
    st.markdown("<br>", unsafe_allow_html=True)

    if not filtered:
        st.info("Nenhum equipamento encontrado com os filtros aplicados.")
        if st.button("➕  Cadastrar Primeiro Equipamento"):
            st.session_state.active_page = "equipment_form"
            st.session_state.form_mode = "new"
            st.rerun()
        return

    # ── Equipment Cards ────────────────────────────────────────
    for i in range(0, len(filtered), 1):
        eq = filtered[i]

        badge_cls = {
            "Ativo": "status-active",
            "Manutenção": "status-maint",
            "Inativo": "status-inactive",
        }.get(eq["status"], "")

        with st.container():
            st.markdown(
                f"""
                <div class="forzy-card" style="margin-bottom:12px;padding:20px 24px;">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;">
                    <div>
                      <span class="tag-badge">{eq['tag']}</span>
                      <span style="font-family:'Barlow Condensed',sans-serif;font-size:22px;font-weight:700;
                                   color:#3D1A6E;margin-left:12px;">{eq['nome']}</span>
                    </div>
                    <span class="status-badge {badge_cls}">{eq['status']}</span>
                  </div>
                  <div style="display:flex;gap:32px;margin-top:14px;flex-wrap:wrap;">
                    <div><span style="color:#888;font-size:11px;text-transform:uppercase;font-weight:600;">Modelo</span>
                         <br><strong style="font-size:13px;">{eq['modelo']}</strong></div>
                    <div><span style="color:#888;font-size:11px;text-transform:uppercase;font-weight:600;">Fabricante</span>
                         <br><strong style="font-size:13px;">{eq['fabricante']}</strong></div>
                    <div><span style="color:#888;font-size:11px;text-transform:uppercase;font-weight:600;">Potência</span>
                         <br><strong style="font-size:13px;color:#FF6B00;">{eq['potencia_kw']} kW / {eq['potencia_cv']} cv</strong></div>
                    <div><span style="color:#888;font-size:11px;text-transform:uppercase;font-weight:600;">Tensão</span>
                         <br><strong style="font-size:13px;">{eq['tensao_v']} V</strong></div>
                    <div><span style="color:#888;font-size:11px;text-transform:uppercase;font-weight:600;">Rotação</span>
                         <br><strong style="font-size:13px;">{eq['rotacao_nominal_rpm']} RPM</strong></div>
                    <div><span style="color:#888;font-size:11px;text-transform:uppercase;font-weight:600;">Local</span>
                         <br><strong style="font-size:13px;">{eq['local_instalacao']}</strong></div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            c1, c2, c3, _ = st.columns([1, 1, 1, 5])
            with c1:
                if st.button("📋 Ficha", key=f"ficha_{eq['id']}"):
                    st.session_state.selected_equipment_id = eq["id"]
                    st.session_state.form_mode = "view"
                    st.session_state.edit_data = eq
                    st.session_state.active_page = "equipment_form"
                    st.rerun()
            with c2:
                if st.button("✏️ Editar", key=f"edit_{eq['id']}"):
                    st.session_state.selected_equipment_id = eq["id"]
                    st.session_state.form_mode = "edit"
                    st.session_state.edit_data = eq
                    st.session_state.active_page = "equipment_form"
                    st.rerun()
            with c3:
                if st.button("📊 Dados", key=f"data_{eq['id']}"):
                    st.session_state.selected_equipment_id = eq["id"]
                    st.session_state.active_page = "raw_data"
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➕  Cadastrar Novo Equipamento"):
        st.session_state.form_mode = "new"
        st.session_state.edit_data = None
        st.session_state.active_page = "equipment_form"
        st.rerun()
