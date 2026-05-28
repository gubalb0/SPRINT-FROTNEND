import streamlit as st
from datetime import datetime, timedelta


def render():
    st.markdown(
        '<div class="topbar-strip">'
        '<div class="strip-seg s1"></div><div class="strip-seg s1"></div>'
        '<div class="strip-seg s2"></div><div class="strip-seg s3"></div>'
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="page-header">'
        "<h1>Central de Alertas</h1>"
        "<p>Monitoramento de eventos e anomalias detectadas nos ativos</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    alertas = st.session_state.get("alertas", [])
    eq_list = st.session_state.get("equipment_list", [])

    # ── KPIs ───────────────────────────────────────────────────
    criticos = sum(1 for a in alertas if a["tipo"] == "critico")
    atencao  = sum(1 for a in alertas if a["tipo"] == "atencao")
    normais  = sum(1 for a in alertas if a["tipo"] == "normal")

    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(
            f'<div class="kpi-card" style="border-top-color:#DC3545;">'
            f'<div class="kpi-icon">🔴</div>'
            f'<div class="kpi-value" style="color:#DC3545;">{criticos}</div>'
            f'<div class="kpi-label">Alertas Críticos</div></div>',
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f'<div class="kpi-card yellow"><div class="kpi-icon">🟡</div>'
            f'<div class="kpi-value">{atencao}</div>'
            f'<div class="kpi-label">Alertas de Atenção</div></div>',
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            f'<div class="kpi-card success"><div class="kpi-icon">🟢</div>'
            f'<div class="kpi-value">{normais}</div>'
            f'<div class="kpi-label">Operando Normal</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Lista de alertas ───────────────────────────────────────
    st.markdown('<div class="section-divider"><span>Eventos Recentes</span></div>', unsafe_allow_html=True)

    ordem = {"critico": 0, "atencao": 1, "normal": 2}
    alertas_ord = sorted(alertas, key=lambda a: ordem.get(a["tipo"], 3))

    for alerta in alertas_ord:
        tipo    = alerta["tipo"]
        cor     = {"critico": "#DC3545", "atencao": "#FFC107", "normal": "#28A745"}.get(tipo)
        bg      = {"critico": "#fff0f0", "atencao": "#fffbf0", "normal": "#f0fff4"}.get(tipo)
        icon    = {"critico": "🔴",      "atencao": "🟡",      "normal": "🟢"}.get(tipo)
        label   = {"critico": "CRÍTICO", "atencao": "ATENÇÃO", "normal": "NORMAL"}.get(tipo)
        eq      = next((e for e in eq_list if e["tag"] == alerta["tag"]), None)
        nome_eq = eq["nome"] if eq else "—"

        st.markdown(
            f"""
            <div style="background:{bg};border-radius:10px;padding:16px 20px;
                        border-left:5px solid {cor};margin-bottom:10px;color:#111;">
              <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                <div style="display:flex;align-items:center;gap:10px;">
                  <span style="font-size:20px;">{icon}</span>
                  <div>
                    <span style="background:{cor};color:white;padding:2px 10px;
                                 border-radius:50px;font-size:11px;font-weight:700;">{label}</span>
                    <span style="background:#FF6B00;color:white;padding:2px 10px;
                                 border-radius:50px;font-size:11px;font-weight:700;margin-left:6px;">{alerta['tag']}</span>
                    <span style="font-weight:700;font-size:14px;margin-left:8px;color:#3D1A6E;">{nome_eq}</span>
                  </div>
                </div>
                <span style="font-size:12px;color:#888;">🕐 {alerta['timestamp']}</span>
              </div>
              <div style="margin-top:8px;font-size:13px;color:#444;">{alerta['mensagem']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if tipo in ("critico", "atencao") and eq:
            if st.button(f"📊 Ver Telemetria — {alerta['tag']}", key=f"alert_btn_{alerta['tag']}"):
                st.session_state.selected_equipment_id = alerta["tag"]
                st.session_state.active_page = "telemetry"
                st.rerun()

    # ── Tabela resumo ──────────────────────────────────────────
    st.markdown('<div class="section-divider"><span>Resumo por Equipamento</span></div>', unsafe_allow_html=True)

    rows_html = ""
    for eq in eq_list:
        saude   = eq.get("saude", "normal")
        cor_s   = {"normal": "#28A745", "atencao": "#FFC107", "critico": "#DC3545"}.get(saude)
        bg_s    = {"normal": "#e6f9ed",  "atencao": "#fff8e6",  "critico": "#fee"}.get(saude)
        label_s = {"normal": "Normal",   "atencao": "Atenção",  "critico": "Crítico"}.get(saude)
        icon_s  = {"normal": "🟢",       "atencao": "🟡",       "critico": "🔴"}.get(saude)
        rows_html += (
            f"<tr>"
            f'<td><span style="background:#FF6B00;color:white;padding:2px 10px;'
            f'border-radius:50px;font-size:11px;font-weight:700;">{eq["tag"]}</span></td>'
            f"<td style='color:#111'>{eq['nome']}</td>"
            f"<td style='color:#111'>{eq.get('planta','—')}</td>"
            f"<td style='color:#111'>{eq['status']}</td>"
            f'<td><span style="background:{bg_s};color:{cor_s};padding:3px 10px;'
            f'border-radius:50px;font-size:11px;font-weight:600;">{icon_s} {label_s}</span></td>'
            f"</tr>"
        )

    st.markdown(
        f"""
        <table class="forzy-table">
          <thead><tr><th>TAG</th><th>Nome</th><th>Planta</th><th>Status</th><th>Saúde</th></tr></thead>
          <tbody>{rows_html}</tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )
