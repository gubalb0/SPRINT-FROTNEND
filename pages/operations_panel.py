"""
PAINEL DE ALERTAS E ESTADOS — página inicial do sistema.

Camada de APRESENTAÇÃO apenas. Consome:
  - services.alert_engine  → detecção de anomalias (modelo analítico)
  - services.nlp_service   → resumos textuais e recomendações (NLP)
  - components.cards       → componentes visuais reutilizáveis

Não contém regra de negócio nem lógica de modelo.
"""

import streamlit as st
from datetime import datetime

from services import alert_engine, nlp_service
from components import cards

INTERVALO_AUTO_SEG = 15


# ═══════════════════════════════════════════════════════════════════════════
# ORQUESTRAÇÃO — executa um ciclo de análise
# ═══════════════════════════════════════════════════════════════════════════
def _executar_ciclo():
    """Dispara o modelo analítico, atualiza estados e gera textos via NLP."""
    ciclo = st.session_state.ciclo_analise

    eventos, estados = alert_engine.detectar_anomalias(ciclo)

    # Detecta quais ativos mudaram de estado neste ciclo
    estados_anteriores = st.session_state.get("estados_ativos", {})
    mudancas = {
        tag: nova
        for tag, nova in estados.items()
        if estados_anteriores.get(tag) and estados_anteriores[tag] != nova
    }

    # Propaga o estado para o cadastro de equipamentos (gestão de estado global)
    for eq in st.session_state.equipment_list:
        if eq["tag"] in estados:
            eq["saude"] = estados[eq["tag"]]

    st.session_state.estados_ativos     = estados
    st.session_state.mudancas_estado    = mudancas
    st.session_state.eventos_novos      = eventos
    st.session_state.historico_eventos  = st.session_state.get("historico_eventos", []) + eventos
    st.session_state.ultima_analise     = datetime.now()

    if ciclo < alert_engine.total_ciclos() - 1:
        st.session_state.ciclo_analise = ciclo + 1


# ═══════════════════════════════════════════════════════════════════════════
# RENDER
# ═══════════════════════════════════════════════════════════════════════════
def render():
    # ── Estado inicial ─────────────────────────────────────────────────────
    if "ciclo_analise" not in st.session_state:
        st.session_state.ciclo_analise = 0
    if "estados_ativos" not in st.session_state:
        _executar_ciclo()

    eq_list = st.session_state.get("equipment_list", [])
    eq_por_tag = {e["tag"]: e for e in eq_list}

    st.markdown(
        '<div class="topbar-strip">'
        '<div class="strip-seg s1"></div><div class="strip-seg s2"></div>'
        '<div class="strip-seg s1"></div><div class="strip-seg s3"></div>'
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="page-header">'
        "<h1>Painel de Alertas e Estados</h1>"
        "<p>Inteligência operacional e apoio à decisão para a equipe de manutenção</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    # ── Barra de controle ──────────────────────────────────────────────────
    c1, c2, c3 = st.columns([1.4, 1.4, 3.2])
    with c1:
        atualizar = st.button("🔄  Atualizar Análise", use_container_width=True)
    with c2:
        auto = st.toggle(f"Auto ({INTERVALO_AUTO_SEG}s)", value=False,
                         help="Executa um ciclo de análise automaticamente")
    with c3:
        ultima = st.session_state.get("ultima_analise")
        ultima_txt = ultima.strftime("%H:%M:%S") if ultima else "—"
        ciclo_atual = st.session_state.ciclo_analise
        total = alert_engine.total_ciclos()
        st.markdown(
            f'<div style="padding-top:9px;font-size:12px;color:#888;">'
            f'Última análise: <b style="color:#FF6B00">{ultima_txt}</b> &nbsp;•&nbsp; '
            f'Ciclo <b>{ciclo_atual}</b> de {total - 1} &nbsp;•&nbsp; '
            f'Modelo: <b>{alert_engine.MODELO_VERSAO}</b></div>',
            unsafe_allow_html=True,
        )

    if atualizar:
        _executar_ciclo()
        st.rerun()

    if st.session_state.ciclo_analise >= alert_engine.total_ciclos() - 1:
        st.markdown(
            '<div style="background:#fff8e6;border-left:4px solid #FFC107;border-radius:8px;'
            'padding:9px 14px;font-size:12px;color:#856404;margin-top:6px;">'
            '⚠️ Cenário de simulação concluído. Use <b>Reiniciar Simulação</b> na barra '
            'lateral para executar novamente.</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Conteúdo dinâmico ──────────────────────────────────────────────────
    if auto and hasattr(st, "fragment"):
        st.fragment(run_every=f"{INTERVALO_AUTO_SEG}s")(_conteudo)(eq_por_tag, auto_on=True)
    else:
        _conteudo(eq_por_tag, auto_on=False)


def _conteudo(eq_por_tag, auto_on=False):
    """Bloco recarregável do painel."""
    if auto_on:
        _executar_ciclo()

    estados   = st.session_state.get("estados_ativos", {})
    novos     = st.session_state.get("eventos_novos", [])
    mudancas  = st.session_state.get("mudancas_estado", {})
    historico = st.session_state.get("historico_eventos", [])
    eq_list   = list(eq_por_tag.values())

    # ── Notificação de novos eventos ───────────────────────────────────────
    for ev in novos:
        nome = eq_por_tag.get(ev["tag"], {}).get("nome", ev["tag"])
        if ev["severidade"] == "critico":
            st.error(f"🚨 **Novo alerta crítico** — {ev['tag']} ({nome}): "
                     f"{ev.get('metrica_label')} em {ev['valor']} {ev.get('unidade','')}")
        elif ev["severidade"] == "atencao":
            st.warning(f"⚠️ **Novo desvio detectado** — {ev['tag']} ({nome}): "
                       f"{ev.get('metrica_label')} em {ev['valor']} {ev.get('unidade','')}")

    for tag, nova in mudancas.items():
        nome = eq_por_tag.get(tag, {}).get("nome", tag)
        lbl = cards.CORES.get(nova, {}).get("label", nova)
        st.info(f"🔁 **Mudança de estado** — {tag} ({nome}) passou para **{lbl}**")

    # ── KPIs ───────────────────────────────────────────────────────────────
    criticos = sum(1 for s in estados.values() if s == "critico")
    atencao  = sum(1 for s in estados.values() if s == "atencao")
    normais  = sum(1 for s in estados.values() if s == "normal")

    k1, k2, k3, k4 = st.columns(4)
    kpis = [
        (k1, criticos,        "Ativos Críticos",   "🔴", "#DC3545"),
        (k2, atencao,         "Em Atenção",         "🟡", "#C89A00"),
        (k3, normais,         "Operando Normal",    "🟢", "#28A745"),
        (k4, len(historico),  "Eventos Registrados","📋", "#3D1A6E"),
    ]
    for col, val, label, icon, cor in kpis:
        with col:
            st.markdown(
                f'<div class="kpi-card" style="border-top-color:{cor};">'
                f'<div class="kpi-icon">{icon}</div>'
                f'<div class="kpi-value" style="color:{cor};">{val}</div>'
                f'<div class="kpi-label">{label}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Resumo executivo (NLP) ─────────────────────────────────────────────
    texto_exec = nlp_service.resumo_executivo(estados, eq_list)
    cards.bloco_resumo_executivo(
        texto_exec,
        nlp_service.MOTOR_NLP,
        st.session_state.ciclo_analise,
        alert_engine.total_ciclos(),
    )

    # ── Alertas ativos ─────────────────────────────────────────────────────
    st.markdown('<div class="section-divider"><span>Alertas Ativos</span></div>',
                unsafe_allow_html=True)

    ativos = [e for e in historico if e["severidade"] in ("critico", "atencao")]
    # mantém apenas o evento mais recente por (tag, métrica)
    vistos, alertas_ativos = set(), []
    for ev in reversed(ativos):
        chave = (ev["tag"], ev["metrica"])
        if chave not in vistos:
            vistos.add(chave)
            alertas_ativos.append(ev)
    ordem = {"critico": 0, "atencao": 1}
    alertas_ativos.sort(key=lambda e: ordem.get(e["severidade"], 2))

    if not alertas_ativos:
        st.markdown(
            '<div style="background:#f0fff4;border-left:5px solid #28A745;border-radius:10px;'
            'padding:18px 22px;color:#1a7a35;font-size:14px;">'
            '🟢 <b>Nenhum alerta ativo.</b> Todos os ativos operam dentro dos parâmetros '
            'nominais. Clique em <b>Atualizar Análise</b> para executar um novo ciclo.</div>',
            unsafe_allow_html=True,
        )
    else:
        ids_novos = {e["id"] for e in st.session_state.get("eventos_novos", [])}
        for ev in alertas_ativos:
            eq = eq_por_tag.get(ev["tag"], {})
            resumo = nlp_service.resumir_evento(ev, eq)
            cards.card_alerta(ev, eq.get("nome", ev["tag"]), resumo, novo=ev["id"] in ids_novos)

            b1, b2, _ = st.columns([1.1, 1.1, 4])
            with b1:
                if st.button("📊 Telemetria", key=f"pa_tel_{ev['id']}"):
                    st.session_state.selected_equipment_id = ev["tag"]
                    st.session_state.active_page = "telemetry"
                    st.rerun()
            with b2:
                if st.button("📋 Ficha", key=f"pa_fic_{ev['id']}"):
                    st.session_state.selected_equipment_id = ev["tag"]
                    st.session_state.form_mode = "view"
                    st.session_state.edit_data = eq
                    st.session_state.active_page = "equipment_form"
                    st.rerun()

    # ── Apoio à decisão ────────────────────────────────────────────────────
    st.markdown('<div class="section-divider"><span>Apoio à Decisão — Ações Recomendadas</span></div>',
                unsafe_allow_html=True)

    if not alertas_ativos:
        st.markdown(
            '<div style="background:#fff;border-radius:12px;padding:20px;text-align:center;'
            'color:#888;font-size:13px;box-shadow:0 3px 14px rgba(0,0,0,0.06);">'
            'Nenhuma ação de manutenção requerida no momento.</div>',
            unsafe_allow_html=True,
        )
    else:
        recs = [nlp_service.recomendar_acao(ev) for ev in alertas_ativos]
        for i in range(0, len(recs), 2):
            bloco = recs[i:i + 2]
            cols = st.columns(len(bloco))
            for col, rec in zip(cols, bloco):
                with col:
                    cards.card_recomendacao(rec)

    # ── Estados operacionais ───────────────────────────────────────────────
    st.markdown('<div class="section-divider"><span>Estado Operacional dos Ativos</span></div>',
                unsafe_allow_html=True)

    ordem_sev = {"critico": 0, "atencao": 1, "normal": 2}
    for eq in sorted(eq_list, key=lambda e: ordem_sev.get(estados.get(e["tag"], "normal"), 3)):
        sev = estados.get(eq["tag"], "normal")
        desc = nlp_service.descrever_estado(eq, sev)
        cards.painel_estado(eq, sev, desc, mudou=eq["tag"] in mudancas)

    # ── Histórico de eventos ───────────────────────────────────────────────
    st.markdown('<div class="section-divider"><span>Histórico de Eventos</span></div>',
                unsafe_allow_html=True)
    cards.timeline_eventos(historico)
