import streamlit as st
from utils.session import PLANTS


def render():
    st.markdown(
        '<div class="topbar-strip">'
        '<div class="strip-seg s2"></div><div class="strip-seg s1"></div>'
        '<div class="strip-seg s2"></div><div class="strip-seg s3"></div>'
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="page-header">'
        "<h1>Navegação por Planta</h1>"
        "<p>Selecione a planta e a área para visualizar os equipamentos instalados</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    eq_list = st.session_state.get("equipment_list", [])

    # ── Cards de Planta ────────────────────────────────────────
    st.markdown('<div class="section-divider"><span>Plantas Disponíveis</span></div>', unsafe_allow_html=True)

    cols = st.columns(len(PLANTS))
    for col, (planta_nome, planta_info) in zip(cols, PLANTS.items()):
        equips_planta = [e for e in eq_list if e.get("planta") == planta_nome]
        criticos = sum(1 for e in equips_planta if e.get("saude") == "critico")
        atencao  = sum(1 for e in equips_planta if e.get("saude") == "atencao")
        normais  = sum(1 for e in equips_planta if e.get("saude") == "normal")

        saude_icon = "🔴" if criticos > 0 else ("🟡" if atencao > 0 else "🟢")

        with col:
            selected = st.session_state.get("planta_selecionada") == planta_nome
            border = "3px solid #FF6B00" if selected else "1px solid #e0e0e0"

            st.markdown(
                f"""
                <div style="background:white;border-radius:12px;padding:20px;
                            box-shadow:0 4px 24px rgba(0,0,0,0.08);
                            border:{border};color:#111;margin-bottom:8px;">
                  <div style="font-size:28px;margin-bottom:8px;">{saude_icon}</div>
                  <div style="font-family:'Barlow Condensed',sans-serif;font-size:20px;
                              font-weight:900;color:#3D1A6E;text-transform:uppercase;">{planta_nome}</div>
                  <div style="margin-top:12px;display:flex;gap:12px;flex-wrap:wrap;">
                    <span style="background:#e6f9ed;color:#1a7a35;padding:3px 10px;
                                 border-radius:50px;font-size:11px;font-weight:700;">
                      🟢 {normais} normal</span>
                    <span style="background:#fff3cd;color:#856404;padding:3px 10px;
                                 border-radius:50px;font-size:11px;font-weight:700;">
                      🟡 {atencao} atenção</span>
                    <span style="background:#fee;color:#c0392b;padding:3px 10px;
                                 border-radius:50px;font-size:11px;font-weight:700;">
                      🔴 {criticos} crítico</span>
                  </div>
                  <div style="margin-top:10px;font-size:12px;color:#888;">
                    {len(equips_planta)} equipamento(s) • {len(planta_info['areas'])} área(s)
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                "✅ Selecionada" if selected else "🏭 Selecionar",
                key=f"plant_{planta_nome}",
                use_container_width=True,
            ):
                st.session_state.planta_selecionada = planta_nome
                st.session_state.area_selecionada = None
                st.rerun()

    # ── Áreas da Planta Selecionada ────────────────────────────
    planta_sel = st.session_state.get("planta_selecionada")
    if not planta_sel:
        st.info("👆 Selecione uma planta acima para ver suas áreas.")
        return

    st.markdown(
        f'<div class="section-divider"><span>Áreas — {planta_sel}</span></div>',
        unsafe_allow_html=True,
    )

    areas = PLANTS[planta_sel]["areas"]
    area_cols = st.columns(len(areas))
    for col, area in zip(area_cols, areas):
        equips_area = [e for e in eq_list if e.get("area") == area]
        criticos_a = sum(1 for e in equips_area if e.get("saude") == "critico")
        saude_icon_a = "🔴" if criticos_a > 0 else ("🟡" if any(e.get("saude") == "atencao" for e in equips_area) else "🟢")
        selected_a = st.session_state.get("area_selecionada") == area

        with col:
            st.markdown(
                f"""
                <div style="background:white;border-radius:10px;padding:16px;
                            box-shadow:0 2px 12px rgba(0,0,0,0.06);
                            border:{'2px solid #FF6B00' if selected_a else '1px solid #e0e0e0'};
                            color:#111;margin-bottom:8px;text-align:center;">
                  <div style="font-size:22px;">{saude_icon_a}</div>
                  <div style="font-weight:700;font-size:13px;margin-top:6px;color:#3D1A6E;">{area}</div>
                  <div style="font-size:11px;color:#888;margin-top:4px;">{len(equips_area)} equip.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                "✅" if selected_a else "Ver área",
                key=f"area_{area}",
                use_container_width=True,
            ):
                st.session_state.area_selecionada = area
                st.rerun()

    # ── Equipamentos da Área ───────────────────────────────────
    area_sel = st.session_state.get("area_selecionada")
    if not area_sel:
        st.info("👆 Selecione uma área para ver os equipamentos.")
        return

    equips_filtrados = [e for e in eq_list if e.get("area") == area_sel]

    st.markdown(
        f'<div class="section-divider"><span>Equipamentos — {area_sel}</span></div>',
        unsafe_allow_html=True,
    )

    if not equips_filtrados:
        st.info("Nenhum equipamento cadastrado nesta área.")
        return

    for eq in equips_filtrados:
        saude = eq.get("saude", "normal")
        saude_color = {"normal": "#28A745", "atencao": "#FFC107", "critico": "#DC3545"}.get(saude, "#28A745")
        saude_bg    = {"normal": "#e6f9ed", "atencao": "#fff8e6", "critico": "#fee"}.get(saude, "#e6f9ed")
        saude_label = {"normal": "Normal", "atencao": "Atenção", "critico": "Crítico"}.get(saude)
        saude_icon2 = {"normal": "🟢", "atencao": "🟡", "critico": "🔴"}.get(saude)

        st.markdown(
            f"""
            <div style="background:white;border-radius:12px;padding:18px 22px;
                        box-shadow:0 4px 16px rgba(0,0,0,0.07);
                        border-left:5px solid {saude_color};
                        margin-bottom:10px;color:#111;">
              <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                <div style="display:flex;align-items:center;gap:12px;">
                  <span style="background:#FF6B00;color:white;padding:4px 12px;border-radius:50px;
                               font-size:12px;font-weight:700;">{eq['tag']}</span>
                  <span style="font-family:'Barlow Condensed',sans-serif;font-size:20px;
                               font-weight:700;color:#3D1A6E;">{eq['nome']}</span>
                </div>
                <span style="background:{saude_bg};color:{saude_color};padding:4px 14px;
                             border-radius:50px;font-size:12px;font-weight:700;">
                  {saude_icon2} {saude_label}
                </span>
              </div>
              <div style="display:flex;gap:24px;margin-top:12px;flex-wrap:wrap;font-size:13px;">
                <span><b>Modelo:</b> {eq['modelo']}</span>
                <span><b>Potência:</b> <span style="color:#FF6B00;font-weight:700">{eq['potencia_kw']} kW</span></span>
                <span><b>Tensão:</b> {eq['tensao_v']} V</span>
                <span><b>Status:</b> {eq['status']}</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        c1, c2, _ = st.columns([1, 1, 6])
        with c1:
            if st.button("📊 Telemetria", key=f"telem_{eq['id']}"):
                st.session_state.selected_equipment_id = eq["id"]
                st.session_state.active_page = "telemetry"
                st.rerun()
        with c2:
            if st.button("📋 Ficha", key=f"fichapl_{eq['id']}"):
                st.session_state.selected_equipment_id = eq["id"]
                st.session_state.form_mode = "view"
                st.session_state.edit_data = eq
                st.session_state.active_page = "equipment_form"
                st.rerun()
