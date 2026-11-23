"""
PAINEL DE ALERTAS E ESTADOS — página inicial do sistema.

Camada de APRESENTAÇÃO apenas. Consome:
  - services.alert_engine  → detecção de anomalias (modelo analítico)
  - services.nlp_service   → resumos textuais e recomendações (NLP)
  - components.cards       → componentes visuais reutilizáveis

Não contém regra de negócio nem lógica de modelo.
"""

import logging

import streamlit as st

from services import alert_engine, nlp_service, monitoring
from components import cards

INTERVALO_AUTO_SEG = 15
log = logging.getLogger("forzy.painel")


def _executar_ciclo_seguro():
    """Executa um ciclo tratando falhas de forma amigável (Sprint 4).

    Se o modelo/serviço falhar, o painel mantém o último estado válido e mostra
    uma mensagem com o trace_id em vez de um traceback do Python.
    """
    try:
        resumo = monitoring.executar_ciclo(st.session_state)
        if resumo["descartados"]:
            st.session_state.aviso_contrato = (
                f"{resumo['descartados']} evento(s) descartado(s) por não respeitarem "
                f"o contrato do modelo (trace_id {resumo['trace_id']})."
            )
        return True
    except Exception as exc:  # noqa: BLE001
        trace_id = monitoring.novo_trace_id()
        log.exception("falha no ciclo de análise trace_id=%s", trace_id)
        st.session_state.erro_ciclo = {"trace_id": trace_id, "tipo": type(exc).__name__}
        return False


# ═══════════════════════════════════════════════════════════════════════════
# RENDER
# ═══════════════════════════════════════════════════════════════════════════
def render():
    # ── Estado inicial ─────────────────────────────────────────────────────
    monitoring.garantir_inicializado(st.session_state)

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
            f'Modelo: <b>{alert_engine.MODELO_VERSAO}</b> &nbsp;•&nbsp; '
            f'trace_id: <code>{st.session_state.get("trace_id", "—")}</code></div>',
            unsafe_allow_html=True,
        )

    if atualizar:
        st.session_state.pop("erro_ciclo", None)
        _executar_ciclo_seguro()
        st.rerun()

    erro = st.session_state.get("erro_ciclo")
    if erro:
        st.error(
            "Não foi possível atualizar a análise agora. Os dados exibidos são do "
            f"último ciclo válido. Se o problema persistir, informe o código "
            f"**{erro['trace_id']}** ao suporte."
        )
    aviso = st.session_state.pop("aviso_contrato", None)
    if aviso:
        st.warning(aviso)

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
        _executar_ciclo_seguro()

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
        (k4, len(monitoring.pendentes(st.session_state)), "Pendentes de Ação", "📌", "#3D1A6E"),
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

    alertas_ativos = monitoring.alertas_ativos(st.session_state)

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
            rec = monitoring.reconhecimento(st.session_state, ev["id"])
            cards.card_alerta(ev, eq.get("nome", ev["tag"]), resumo,
                              novo=ev["id"] in ids_novos, reconhecimento=rec)

            b0, b1, b2, b3, b4, _ = st.columns([1.3, 1.1, 0.9, 0.55, 0.55, 1.6])
            with b0:
                if rec is None:
                    if st.button("✔ Reconhecer", key=f"pa_ack_{ev['id']}", type="primary"):
                        monitoring.reconhecer_alerta(st.session_state, ev["id"])
                        st.rerun()
                else:
                    st.markdown(
                        f'<div style="padding-top:8px;font-size:12px;color:#28A745;font-weight:700;">'
                        f'✔ Reconhecido {rec["hora"].strftime("%H:%M:%S")}</div>',
                        unsafe_allow_html=True,
                    )
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
            fb = monitoring.feedback(st.session_state, ev["id"])
            if fb is None:
                with b3:
                    if st.button("👍", key=f"pa_fb_up_{ev['id']}", help="O resumo de IA foi útil"):
                        monitoring.registrar_feedback(st.session_state, ev["id"], True)
                        st.rerun()
                with b4:
                    if st.button("👎", key=f"pa_fb_dn_{ev['id']}", help="O resumo de IA não ajudou"):
                        monitoring.registrar_feedback(st.session_state, ev["id"], False)
                        st.rerun()
            else:
                with b3:
                    st.markdown(
                        '<div style="padding-top:8px;font-size:11px;color:#888;white-space:nowrap;">'
                        f'{"👍" if fb["util"] else "👎"} feedback registrado</div>',
                        unsafe_allow_html=True,
                    )

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
