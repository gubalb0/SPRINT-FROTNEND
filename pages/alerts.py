"""
HISTÓRICO DE EVENTOS — Sprint 4.

Na Sprint 3 esta página lia `st.session_state.alertas`, uma lista estática criada
na Sprint 2, e por isso mostrava valores diferentes do Painel de Alertas
(ex.: MTR-002 a 82 °C aqui e 84,3 °C no painel). Agora ela consome o mesmo
histórico produzido por `services.monitoring`, com filtros, status de
reconhecimento, feedback de IA e exportação CSV.
"""

import pandas as pd
import streamlit as st

from components import cards
from services import monitoring


def _linhas(historico, eq_por_tag):
    linhas = []
    for ev in reversed(historico):
        rec = monitoring.reconhecimento(st.session_state, ev["id"])
        fb = monitoring.feedback(st.session_state, ev["id"])
        linhas.append({
            "Hora": ev["timestamp"].strftime("%H:%M:%S"),
            "Severidade": cards.CORES.get(ev["severidade"], {}).get("label", ev["severidade"]),
            "TAG": ev["tag"],
            "Equipamento": eq_por_tag.get(ev["tag"], {}).get("nome", "—"),
            "Sensor": ev.get("metrica_label", ev["metrica"]),
            "Medido": f'{ev["valor"]} {ev.get("unidade", "")}',
            "Limite": f'{ev["limite"]} {ev.get("unidade", "")}',
            "Score": f'{ev["score_anomalia"] * 100:.0f}%',
            "Reconhecido": rec["hora"].strftime("%H:%M:%S") if rec else "—",
            "Feedback IA": ("👍" if fb["util"] else "👎") if fb else "—",
            "trace_id": ev.get("trace_id", "—"),
            "_sev": ev["severidade"],
        })
    return linhas


def render():
    monitoring.garantir_inicializado(st.session_state)

    st.markdown(
        '<div class="topbar-strip">'
        '<div class="strip-seg s1"></div><div class="strip-seg s1"></div>'
        '<div class="strip-seg s2"></div><div class="strip-seg s3"></div>'
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="page-header">'
        "<h1>Histórico de Eventos</h1>"
        "<p>Rastreabilidade de todos os eventos detectados pelo modelo analítico</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    historico = st.session_state.get("historico_eventos", [])
    eq_por_tag = {e["tag"]: e for e in st.session_state.get("equipment_list", [])}

    # ── KPIs ───────────────────────────────────────────────────
    feedbacks = st.session_state.get("feedback_nlp", {})
    uteis = sum(1 for f in feedbacks.values() if f["util"])
    kpis = [
        (sum(1 for e in historico if e["severidade"] == "critico"), "Eventos Críticos", "🔴", "#DC3545"),
        (sum(1 for e in historico if e["severidade"] == "atencao"), "Eventos de Atenção", "🟡", "#C89A00"),
        (len(st.session_state.get("reconhecimentos", {})), "Reconhecidos", "✔️", "#28A745"),
        (f"{uteis}/{len(feedbacks)}" if feedbacks else "—", "Resumos de IA úteis", "🧠", "#3D1A6E"),
    ]
    for col, (val, label, icon, cor) in zip(st.columns(4), kpis):
        with col:
            st.markdown(
                f'<div class="kpi-card" style="border-top-color:{cor};">'
                f'<div class="kpi-icon">{icon}</div>'
                f'<div class="kpi-value" style="color:{cor};">{val}</div>'
                f'<div class="kpi-label">{label}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    if not historico:
        st.info("Nenhum evento registrado ainda. Execute um ciclo em **Painel de Alertas → Atualizar Análise**.")
        return

    # ── Filtros ────────────────────────────────────────────────
    st.markdown('<div class="section-divider"><span>Eventos</span></div>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns([1.4, 1.4, 1.2])
    with f1:
        sev = st.multiselect("Severidade", ["CRÍTICO", "ATENÇÃO"], default=["CRÍTICO", "ATENÇÃO"])
    with f2:
        tags = st.multiselect("Equipamento (TAG)", sorted(eq_por_tag), default=sorted(eq_por_tag))
    with f3:
        so_pendentes = st.toggle("Só não reconhecidos", value=False)

    linhas = [
        l for l in _linhas(historico, eq_por_tag)
        if l["Severidade"] in sev and l["TAG"] in tags
        and (not so_pendentes or l["Reconhecido"] == "—")
    ]

    if not linhas:
        st.info("Nenhum evento corresponde aos filtros selecionados.")
        return

    df = pd.DataFrame(linhas)
    cor_sev = {s["label"]: s["bg"] for s in cards.CORES.values()}

    def _pinta(row):
        return [f"background-color:{cor_sev.get(row['Severidade'], '#fff')};color:#111"] * len(row)

    vis = df.drop(columns=["_sev"])
    st.dataframe(vis.style.apply(_pinta, axis=1), use_container_width=True, hide_index=True)

    st.download_button(
        "⬇️  Exportar CSV",
        vis.to_csv(index=False).encode("utf-8-sig"),
        file_name="forzy_historico_eventos.csv",
        mime="text/csv",
    )

    # ── Atalho para telemetria ────────────────────────────────
    st.markdown('<div class="section-divider"><span>Investigar Ativo</span></div>', unsafe_allow_html=True)
    cols = st.columns(len(eq_por_tag) or 1)
    for col, tag in zip(cols, sorted(eq_por_tag)):
        with col:
            if st.button(f"📊 Telemetria — {tag}", key=f"hist_tel_{tag}", use_container_width=True):
                st.session_state.selected_equipment_id = tag
                st.session_state.active_page = "telemetry"
                st.rerun()
