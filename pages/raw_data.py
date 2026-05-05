import streamlit as st
import random
import math
from datetime import datetime, timedelta


def _simulate_sensor_data(eq):
    """Generate realistic mock sensor readings based on equipment nominal values."""
    t = datetime.now()
    # Simulate slight variation around nominal values
    noise = lambda val, pct: val * (1 + random.uniform(-pct, pct))

    rpm_nom = eq.get("rotacao_nominal_rpm", 1760)
    v_nom   = eq.get("tensao_v", 380)
    i_nom   = eq.get("corrente_nominal_a", 22.5)
    fp      = eq.get("fator_potencia", 0.87)

    # Raw ADC values (simulated 12-bit ADC: 0–4095)
    raw_v  = int(noise(2800, 0.03))   # maps to voltage
    raw_i  = int(noise(1640, 0.05))   # maps to current
    raw_rpm = int(noise(3100, 0.02))  # maps to RPM via encoder
    raw_temp = int(noise(890, 0.04))  # maps to temperature (°C)
    raw_vib = int(noise(310, 0.10))   # maps to vibration (mm/s)

    # Conversion factors (calibrated per sensor)
    v_factor   = v_nom / 2800
    i_factor   = i_nom / 1640
    rpm_factor = rpm_nom / 3100
    temp_factor = 120.0 / 4095
    vib_factor  = 20.0 / 4095

    volts   = round(raw_v * v_factor, 1)
    amperes = round(raw_i * i_factor, 2)
    rpm     = round(raw_rpm * rpm_factor)
    temp_c  = round(raw_temp * temp_factor, 1)
    vib_mms = round(raw_vib * vib_factor, 2)
    pot_kw  = round(volts * amperes * math.sqrt(3) * fp / 1000, 2)

    return {
        "timestamp": t.strftime("%Y-%m-%d %H:%M:%S"),
        "raw": {
            "ADC_V":   raw_v,
            "ADC_I":   raw_i,
            "ADC_RPM": raw_rpm,
            "ADC_T":   raw_temp,
            "ADC_VIB": raw_vib,
        },
        "converted": {
            "tensao_v":     (volts,   "V",     v_nom,    v_nom * 0.95, v_nom * 1.05),
            "corrente_a":   (amperes, "A",     i_nom,    0,            i_nom * 1.10),
            "rotacao_rpm":  (rpm,     "RPM",   rpm_nom,  rpm_nom*0.97, rpm_nom*1.03),
            "temperatura_c":(temp_c,  "°C",    None,     0,            80),
            "vibracao_mms": (vib_mms, "mm/s",  None,     0,            4.5),
            "potencia_kw":  (pot_kw,  "kW",    eq.get("potencia_kw", 0), 0, eq.get("potencia_kw", 0)*1.15),
        },
    }


def _status_color(value, low, high):
    if value < low or value > high:
        return "#DC3545"   # danger
    margin = (high - low) * 0.1
    if value < low + margin or value > high - margin:
        return "#FFC107"   # warning
    return "#28A745"       # ok


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
        "<h1>Visualização de Dados Brutos</h1>"
        "<p>Conversão de sinais dos sensores para unidades de engenharia</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    eq_list = st.session_state.get("equipment_list", [])
    if not eq_list:
        st.warning("Nenhum equipamento cadastrado. Cadastre um equipamento primeiro.")
        if st.button("➕ Cadastrar Equipamento"):
            st.session_state.active_page = "equipment_form"
            st.session_state.form_mode = "new"
            st.rerun()
        return

    # ── Equipment Selector ─────────────────────────────────────
    sel_id = st.session_state.get("selected_equipment_id")
    tag_map = {e["tag"]: e for e in eq_list}
    tag_list = list(tag_map.keys())

    default_idx = 0
    if sel_id and sel_id in tag_map:
        default_idx = tag_list.index(sel_id)

    sel_tag = st.selectbox(
        "Selecione o equipamento",
        tag_list,
        index=default_idx,
        format_func=lambda t: f"{t} — {tag_map[t]['nome']}",
    )
    eq = tag_map[sel_tag]
    st.session_state.selected_equipment_id = sel_tag

    # ── Simulate / Refresh ─────────────────────────────────────
    col_btn, col_note = st.columns([1, 5])
    with col_btn:
        refresh = st.button("🔄  Simular Leitura", use_container_width=True)
    with col_note:
        st.markdown(
            '<p style="font-size:12px;color:#888;margin-top:10px;">'
            "⚠️ Dados simulados — integração com sensores reais prevista para próximas sprints.</p>",
            unsafe_allow_html=True,
        )

    if "sensor_data" not in st.session_state or refresh or st.session_state.get("sensor_eq") != sel_tag:
        st.session_state.sensor_data = _simulate_sensor_data(eq)
        st.session_state.sensor_eq = sel_tag

    data = st.session_state.sensor_data
    ts   = data["timestamp"]

    st.markdown(
        f'<p style="font-size:12px;color:#888;margin:4px 0 20px;">Última leitura: <strong>{ts}</strong></p>',
        unsafe_allow_html=True,
    )

    # ── Converted Values — Sensor Cards ───────────────────────
    st.markdown('<div class="section-divider"><span>Valores Convertidos — Unidades de Engenharia</span></div>', unsafe_allow_html=True)

    labels = {
        "tensao_v":      "⚡ Tensão",
        "corrente_a":    "🔌 Corrente",
        "rotacao_rpm":   "🔁 Rotação",
        "temperatura_c": "🌡️ Temperatura",
        "vibracao_mms":  "📳 Vibração",
        "potencia_kw":   "💡 Potência Ativa",
    }

    conv = data["converted"]
    keys = list(conv.keys())

    for row_start in range(0, len(keys), 3):
        row_keys = keys[row_start:row_start + 3]
        cols = st.columns(len(row_keys))
        for col, key in zip(cols, row_keys):
            val, unit, nominal, low, high = conv[key]
            color = _status_color(val, low, high)
            nom_line = f"<div style='font-size:11px;color:#666;margin-top:6px;'>Nominal: {nominal} {unit}</div>" if nominal else ""
            status_dot = "🔴" if color == "#DC3545" else ("🟡" if color == "#FFC107" else "🟢")
            with col:
                st.markdown(
                    f"""
                    <div class="sensor-card">
                      <div class="sensor-status"></div>
                      <div style="font-size:12px;font-weight:700;text-transform:uppercase;
                                  letter-spacing:2px;color:#888;margin-bottom:8px;">
                        {labels[key]}
                      </div>
                      <div class="sensor-value" style="color:{color};">{val}</div>
                      <div class="sensor-unit">{unit}</div>
                      {nom_line}
                      <div style="margin-top:8px;font-size:18px;">{status_dot}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Raw ADC Values ─────────────────────────────────────────
    with st.expander("🔢  Valores Brutos (ADC — 0 a 4095)", expanded=False):
        st.markdown(
            """
            <div class="forzy-card" style="background:#111;color:#eee;">
              <h3 style="color:#FF6B00;">Sinais Raw dos Sensores</h3>
              <p style="font-size:12px;color:#888;margin-bottom:16px;">
                Valores inteiros de 12 bits lidos diretamente pelo microcontrolador antes da conversão.
                Cada canal é calibrado com um fator de escala específico ao tipo de sensor instalado.
              </p>
            """,
            unsafe_allow_html=True,
        )

        raw = data["raw"]
        raw_cols = st.columns(len(raw))
        for col, (k, v_raw) in zip(raw_cols, raw.items()):
            with col:
                pct = v_raw / 4095 * 100
                st.markdown(
                    f"""
                    <div style="text-align:center;padding:12px 8px;">
                      <div style="font-family:'Barlow Condensed',sans-serif;font-size:32px;
                                  font-weight:900;color:#FF6B00;">{v_raw}</div>
                      <div style="font-size:11px;color:#aaa;margin:4px 0 8px;">{k}</div>
                      <div style="background:#333;border-radius:4px;height:6px;">
                        <div style="background:#FF6B00;border-radius:4px;height:6px;width:{pct:.0f}%"></div>
                      </div>
                      <div style="font-size:10px;color:#666;margin-top:4px;">{pct:.1f}% do fundo de escala</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Conversion Formula Reference ───────────────────────────
    with st.expander("📐  Tabela de Conversão / Fatores de Escala", expanded=False):
        st.markdown('<div class="forzy-card"><h3>Fatores de Conversão Aplicados</h3>', unsafe_allow_html=True)

        v_nom = eq["tensao_v"]
        i_nom = eq["corrente_nominal_a"]
        rpm_nom = eq["rotacao_nominal_rpm"]

        rows = [
            ("ADC_V",   "Tensão",      f"ADC × ({v_nom} / 2800)",   "Volts (V)"),
            ("ADC_I",   "Corrente",    f"ADC × ({i_nom} / 1640)",    "Ampères (A)"),
            ("ADC_RPM", "Rotação",     f"ADC × ({rpm_nom} / 3100)",  "RPM"),
            ("ADC_T",   "Temperatura", "ADC × (120 / 4095)",          "°C"),
            ("ADC_VIB", "Vibração",    "ADC × (20 / 4095)",           "mm/s"),
        ]

        rows_html = "".join(
            f"<tr><td><code>{r[0]}</code></td><td>{r[1]}</td>"
            f"<td><code style='font-size:11px'>{r[2]}</code></td><td><strong>{r[3]}</strong></td></tr>"
            for r in rows
        )

        st.markdown(
            f"""
            <table class="forzy-table">
              <thead>
                <tr><th>Canal ADC</th><th>Grandeza</th><th>Fórmula</th><th>Unidade</th></tr>
              </thead>
              <tbody>{rows_html}</tbody>
            </table>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Historical Trend placeholder ───────────────────────────
    st.markdown('<div class="section-divider"><span>Histórico de Leituras</span></div>', unsafe_allow_html=True)

    n = 20
    now = datetime.now()
    times = [(now - timedelta(minutes=i * 5)).strftime("%H:%M") for i in range(n, 0, -1)]
    nom_rpm = eq["rotacao_nominal_rpm"]
    rpm_series = [nom_rpm * (1 + random.uniform(-0.02, 0.02)) for _ in range(n)]
    nom_i = eq["corrente_nominal_a"]
    i_series = [nom_i * (1 + random.uniform(-0.05, 0.05)) for _ in range(n)]

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        import pandas as pd
        df_rpm = pd.DataFrame({"RPM": rpm_series}, index=times)
        st.markdown("**Rotação (RPM) — últimas 20 leituras**")
        st.line_chart(df_rpm, color="#FF6B00", height=200)

    with chart_col2:
        df_i = pd.DataFrame({"Corrente (A)": i_series}, index=times)
        st.markdown("**Corrente (A) — últimas 20 leituras**")
        st.line_chart(df_i, color="#3D1A6E", height=200)

    st.markdown(
        '<p style="font-size:11px;color:#aaa;text-align:center;margin-top:8px;">'
        "Dados históricos simulados — integração com banco de séries temporais prevista para Sprint 2.</p>",
        unsafe_allow_html=True,
    )
