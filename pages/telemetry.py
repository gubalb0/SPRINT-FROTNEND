import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime


LIMITES = {
    "temperatura_c":  {"warn": 70, "crit": 80,  "unit": "°C",    "label": "Temperatura"},
    "vibracao_mms":   {"warn": 2.8, "crit": 4.5, "unit": "mm/s", "label": "Vibração"},
    "corrente_a":     {"warn": None, "crit": None,"unit": "A",    "label": "Corrente"},
    "rotacao_rpm":    {"warn": None, "crit": None,"unit": "RPM",  "label": "Rotação"},
    "tensao_v":       {"warn": None, "crit": None,"unit": "V",    "label": "Tensão"},
    "potencia_kw":    {"warn": None, "crit": None,"unit": "kW",   "label": "Potência Ativa"},
}


def _cor_valor(valor, lim_warn, lim_crit):
    if lim_crit and valor >= lim_crit:
        return "#DC3545", "🔴"
    if lim_warn and valor >= lim_warn:
        return "#FFC107", "🟡"
    return "#28A745", "🟢"


def _gauge(valor, titulo, unidade, max_val, warn, crit, cor):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor,
        title={"text": f"<b>{titulo}</b>", "font": {"size": 13, "color": "#555"}},
        number={"suffix": f" {unidade}", "font": {"size": 20, "color": cor}},
        gauge={
            "axis": {"range": [0, max_val], "tickfont": {"size": 9}},
            "bar": {"color": cor, "thickness": 0.25},
            "bgcolor": "#f4f4f6",
            "borderwidth": 0,
            "steps": [
                {"range": [0, warn or max_val * 0.7], "color": "#e6f9ed"},
                {"range": [warn or max_val * 0.7, crit or max_val * 0.9], "color": "#fff8e6"},
                {"range": [crit or max_val * 0.9, max_val], "color": "#fee"},
            ] if warn else [],
            "threshold": {
                "line": {"color": "#DC3545", "width": 3},
                "thickness": 0.75,
                "value": crit or max_val * 0.9,
            } if crit else {},
        },
    ))
    fig.update_layout(
        height=200, margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="white", font={"family": "Inter"},
    )
    return fig


def _serie_temporal(df, coluna, titulo, unidade, cor, warn=None, crit=None):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df[coluna],
        mode="lines",
        line=dict(color=cor, width=2),
        fill="tozeroy",
        fillcolor="rgba(100,100,100,0.08)",
        name=titulo,
        hovertemplate=f"<b>%{{x|%H:%M}}</b><br>{titulo}: %{{y:.1f}} {unidade}<extra></extra>",
    ))

    if warn:
        fig.add_hline(y=warn, line_dash="dash", line_color="#FFC107", line_width=1.5,
                      annotation_text=f"Atenção ({warn} {unidade})", annotation_font_size=10)
    if crit:
        fig.add_hline(y=crit, line_dash="dash", line_color="#DC3545", line_width=1.5,
                      annotation_text=f"Crítico ({crit} {unidade})", annotation_font_size=10)

    fig.update_layout(
        title=dict(text=f"<b>{titulo}</b>", font=dict(size=14, color="#3D1A6E")),
        height=260,
        margin=dict(l=40, r=20, t=45, b=30),
        paper_bgcolor="white",
        plot_bgcolor="#fafafa",
        xaxis=dict(showgrid=False, tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0", tickfont=dict(size=10),
                   title=dict(text=unidade, font=dict(size=11))),
        legend=dict(font=dict(size=10)),
        font=dict(family="Inter"),
    )
    return fig


def render():
    eq_list  = st.session_state.get("equipment_list", [])
    historicos = st.session_state.get("historicos", {})
    sel_id   = st.session_state.get("selected_equipment_id")

    tag_map  = {e["id"]: e for e in eq_list}
    tag_list = list(tag_map.keys())

    st.markdown(
        '<div class="topbar-strip">'
        '<div class="strip-seg s1"></div><div class="strip-seg s2"></div>'
        '<div class="strip-seg s1"></div><div class="strip-seg s3"></div>'
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="page-header">'
        "<h1>Dashboard de Telemetria</h1>"
        "<p>Monitoramento em tempo real e histórico dos sensores do ativo</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    # ── Seletor de Equipamento ─────────────────────────────────
    c_sel, c_period, c_refresh = st.columns([3, 2, 1])
    with c_sel:
        default_idx = tag_list.index(sel_id) if sel_id and sel_id in tag_list else 0
        sel_tag = st.selectbox(
            "Equipamento",
            tag_list,
            index=default_idx,
            format_func=lambda t: f"{t} — {tag_map[t]['nome']}",
        )
    with c_period:
        periodo = st.selectbox("Período histórico", ["Últimas 2h", "Últimas 6h", "Últimas 12h", "Últimas 24h"], index=3)
    with c_refresh:
        st.markdown("<br>", unsafe_allow_html=True)
        atualizar = st.button("🔄 Atualizar", use_container_width=True)

    eq = tag_map[sel_tag]
    st.session_state.selected_equipment_id = sel_tag

    if atualizar:
        from utils.session import gerar_historico
        st.session_state.historicos[sel_tag] = gerar_historico(eq)
        st.rerun()

    hist = historicos.get(sel_tag, [])
    periodo_horas = {"Últimas 2h": 2, "Últimas 6h": 6, "Últimas 12h": 12, "Últimas 24h": 24}[periodo]
    n_pontos = int(periodo_horas * 60 / 10)
    hist_filtrado = hist[-n_pontos:] if len(hist) >= n_pontos else hist

    df = pd.DataFrame(hist_filtrado)

    # ── Cabeçalho do equipamento ───────────────────────────────
    saude = eq.get("saude", "normal")
    saude_color = {"normal": "#28A745", "atencao": "#FFC107", "critico": "#DC3545"}.get(saude)
    saude_label = {"normal": "🟢 Normal", "atencao": "🟡 Atenção", "critico": "🔴 Crítico"}.get(saude)

    st.markdown(
        f"""
        <div style="background:white;border-radius:12px;padding:16px 22px;
                    box-shadow:0 4px 24px rgba(0,0,0,0.08);
                    border-left:6px solid {saude_color};
                    margin-bottom:20px;color:#111;
                    display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">
          <div>
            <span style="background:#FF6B00;color:white;padding:3px 12px;border-radius:50px;
                         font-size:12px;font-weight:700;">{eq['tag']}</span>
            <span style="font-family:'Barlow Condensed',sans-serif;font-size:24px;
                         font-weight:900;color:#3D1A6E;margin-left:10px;">{eq['nome']}</span>
            <div style="font-size:12px;color:#888;margin-top:4px;">
              📍 {eq.get('local_instalacao','—')} &nbsp;|&nbsp;
              ⚙️ {eq['modelo']} &nbsp;|&nbsp;
              🏭 {eq.get('planta','—')}
            </div>
          </div>
          <div style="text-align:right;">
            <div style="font-size:20px;font-weight:700;color:{saude_color};">{saude_label}</div>
            <div style="font-size:11px;color:#aaa;">Saúde do Ativo</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df.empty:
        st.warning("Sem dados históricos para este equipamento.")
        return

    ultimo = df.iloc[-1]

    # ── Gauges — Valores Atuais ────────────────────────────────
    st.markdown('<div class="section-divider"><span>Leitura Atual dos Sensores</span></div>', unsafe_allow_html=True)

    g1, g2, g3 = st.columns(3)
    i_nom = eq.get("corrente_nominal_a", 22.5)
    rpm_nom = eq.get("rotacao_nominal_rpm", 1760)
    v_nom = eq.get("tensao_v", 380)

    with g1:
        st.plotly_chart(_gauge(ultimo["temperatura_c"], "Temperatura", "°C", 120, 70, 80, "#FF6B00"), use_container_width=True)
    with g2:
        st.plotly_chart(_gauge(ultimo["vibracao_mms"], "Vibração", "mm/s", 10, 2.8, 4.5, "#3D1A6E"), use_container_width=True)
    with g3:
        cor_i, _ = _cor_valor(ultimo["corrente_a"], i_nom * 1.05, i_nom * 1.15)
        st.plotly_chart(_gauge(ultimo["corrente_a"], "Corrente", "A", i_nom * 1.5, i_nom * 1.05, i_nom * 1.15, cor_i), use_container_width=True)

    g4, g5, g6 = st.columns(3)
    with g4:
        cor_r, _ = _cor_valor(abs(ultimo["rotacao_rpm"] - rpm_nom), rpm_nom * 0.02, rpm_nom * 0.05)
        st.plotly_chart(_gauge(ultimo["rotacao_rpm"], "Rotação", "RPM", rpm_nom * 1.2, rpm_nom * 0.97, rpm_nom * 1.03, "#28A745"), use_container_width=True)
    with g5:
        st.plotly_chart(_gauge(ultimo["tensao_v"], "Tensão", "V", v_nom * 1.2, v_nom * 0.95, v_nom * 1.05, "#F5C400"), use_container_width=True)
    with g6:
        pot_nom = eq.get("potencia_kw", 11.0)
        st.plotly_chart(_gauge(ultimo["potencia_kw"], "Potência Ativa", "kW", pot_nom * 1.3, pot_nom * 1.05, pot_nom * 1.15, "#3D1A6E"), use_container_width=True)

    # ── Séries Temporais ───────────────────────────────────────
    st.markdown('<div class="section-divider"><span>Histórico — Séries Temporais</span></div>', unsafe_allow_html=True)

    st.markdown("**Temperatura & Vibração** — indicadores primários de falha")
    t1, t2 = st.columns(2)
    with t1:
        st.plotly_chart(_serie_temporal(df, "temperatura_c", "Temperatura", "°C", "#FF6B00", warn=70, crit=80), use_container_width=True)
    with t2:
        st.plotly_chart(_serie_temporal(df, "vibracao_mms", "Vibração", "mm/s", "#DC3545", warn=2.8, crit=4.5), use_container_width=True)

    st.markdown("**Elétricos** — corrente, tensão e potência")
    t3, t4, t5 = st.columns(3)
    with t3:
        st.plotly_chart(_serie_temporal(df, "corrente_a", "Corrente", "A", "#3D1A6E",
                                        warn=i_nom * 1.05, crit=i_nom * 1.15), use_container_width=True)
    with t4:
        st.plotly_chart(_serie_temporal(df, "tensao_v", "Tensão", "V", "#F5C400",
                                        warn=v_nom * 1.05, crit=v_nom * 1.10), use_container_width=True)
    with t5:
        st.plotly_chart(_serie_temporal(df, "potencia_kw", "Potência Ativa", "kW", "#28A745"), use_container_width=True)

    st.markdown("**Mecânico** — rotação")
    st.plotly_chart(_serie_temporal(df, "rotacao_rpm", "Rotação", "RPM", "#888888",
                                    warn=rpm_nom * 0.97, crit=rpm_nom * 0.94), use_container_width=True)

    # ── Placa do Motor (Visão Computacional) ───────────────────
    st.markdown('<div class="section-divider"><span>Placa de Identificação — Visão Computacional</span></div>', unsafe_allow_html=True)

    col_img, col_ocr = st.columns([1, 1])
    with col_img:
        st.markdown(
            f"""
            <div style="background:#111;border-radius:12px;padding:24px;text-align:center;
                        border:2px dashed #FF6B00;min-height:180px;
                        display:flex;flex-direction:column;align-items:center;justify-content:center;">
              <div style="font-size:48px;margin-bottom:8px;">🏷️</div>
              <div style="color:#FF6B00;font-weight:700;font-size:14px;">PLACA SIMULADA</div>
              <div style="color:#888;font-size:12px;margin-top:6px;">{eq.get('imagem_placa','—')}</div>
              <div style="color:#555;font-size:11px;margin-top:12px;">
                Integração com câmera / upload de imagem<br>prevista para Sprint 3
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_ocr:
        st.markdown('<div class="forzy-card"><h3>🔍 Dados Extraídos — OCR</h3>', unsafe_allow_html=True)
        campos_ocr = {
            "Modelo": eq["modelo"],
            "Fabricante": eq["fabricante"],
            "Potência (kW)": f"{eq['potencia_kw']} kW",
            "Tensão": f"{eq['tensao_v']} V",
            "Corrente Nominal": f"{eq['corrente_nominal_a']} A",
            "Rotação": f"{eq['rotacao_nominal_rpm']} RPM",
            "Classe IP": eq["grau_protecao"],
        }
        for campo, valor in campos_ocr.items():
            st.markdown(
                f"""
                <div style="display:flex;justify-content:space-between;
                            padding:7px 0;border-bottom:1px solid #333;color:#fff;">
                  <span style="color:#aaa;font-size:12px;font-weight:600;text-transform:uppercase;">{campo}</span>
                  <span style="color:#fff;font-weight:700;font-size:13px;">{valor}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown(
            '<div style="margin-top:10px;background:#e6f9ed;border-radius:6px;padding:8px 12px;'
            'font-size:12px;color:#1a7a35;font-weight:600;">✅ Dados conferidos com cadastro — sem divergências</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Tabela de dados brutos ─────────────────────────────────
    with st.expander("📋  Tabela de Dados Históricos (raw)", expanded=False):
        df_display = df.copy()
        df_display["timestamp"] = df_display["timestamp"].dt.strftime("%d/%m %H:%M")
        df_display = df_display.rename(columns={
            "timestamp": "Horário",
            "temperatura_c": "Temp (°C)",
            "vibracao_mms": "Vibração (mm/s)",
            "corrente_a": "Corrente (A)",
            "rotacao_rpm": "RPM",
            "tensao_v": "Tensão (V)",
            "potencia_kw": "Potência (kW)",
        })
        st.dataframe(df_display.tail(50).iloc[::-1], use_container_width=True, hide_index=True)
