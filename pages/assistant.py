"""
Assistente de Troubleshooting (Sprint 4 — Governança do assistente).

A página só exibe o que o serviço `services/assistant.py` devolve. Filtro por
perfil, regra de citação e log de auditoria ficam no serviço, não na tela.
"""

import html

import streamlit as st

from services import access, assistant
from services.knowledge_base import KB_VERSION

EXEMPLOS = [
    "O que devo fazer com o MTR-002?",
    "Qual o valor bruto do ADC do MTR-002?",
    "Como calibrar o inversor de frequência do MTR-002?",
    "Como fazer a lubrificação dos rolamentos?",
    "Posso ajustar o threshold de vibração do MTR-002?",
]

COR = {"COM_FONTE": "#28A745", "SEM_FONTE_REVISAO": "#FF6B00", "ACESSO_NEGADO": "#6c757d"}
ROTULO = {"COM_FONTE": "✅ Com fonte", "SEM_FONTE_REVISAO": "🧑‍🔧 Sem fonte — revisão humana",
          "ACESSO_NEGADO": "🔒 Acesso negado ao perfil"}


def _e(t):
    return html.escape(str(t))


def _perguntar(pergunta):
    perfil = st.session_state.perfil
    resp = assistant.perguntar(st.session_state, perfil, st.session_state.user_id, pergunta,
                               tag=st.session_state.get("assist_tag"))
    resp["pergunta"] = pergunta
    st.session_state.setdefault("chat_assistente", []).append(resp)


def _render_resposta(i, r):
    st.markdown(
        f'<div style="background:#f3eff9;border-radius:10px;padding:10px 14px;margin:14px 0 6px;color:#3D1A6E;">'
        f'<b>🧑 {access.PERFIS[r["perfil"]]}:</b> {_e(r["pergunta"])}</div>', unsafe_allow_html=True)

    status = r["citation_status"]
    cor = COR[status]
    corpo = [f'<div style="font-size:11px;font-weight:800;color:{cor};letter-spacing:.4px;">{ROTULO[status]}'
             + (f' · handoff {r["handoff_level"]}' if r["handoff_level"] else "") + "</div>",
             f'<div style="font-size:15px;margin:6px 0 10px;color:#111;">{_e(r["texto"])}</div>']
    if r["citacoes"]:
        itens = "".join(
            f'<li><b>{_e(c["titulo"])}</b> ({_e(c["doc_id"])}, versão {_e(c["doc_version"])}), '
            f'seção “{_e(c["secao"])}” · similaridade {c["similaridade"]:.2f}</li>' for c in r["citacoes"])
        corpo.append(f'<div style="font-size:12.5px;color:#333;"><b>📄 Fonte documental</b><ul style="margin:4px 0 8px;">{itens}</ul></div>')
    if r["dado_operacional"]:
        itens = "".join(f"<li>{_e(d)}</li>" for d in r["dado_operacional"])
        corpo.append(f'<div style="font-size:12.5px;color:#333;"><b>📈 Dado operacional</b><ul style="margin:4px 0 8px;">{itens}</ul></div>')
    corpo.append(f'<div style="font-size:11px;color:#888;">Rastreio: trace_id {r["trace_id"]} · base de conhecimento v{KB_VERSION}</div>')
    st.markdown(f'<div style="background:white;border-left:6px solid {cor};border-radius:10px;padding:12px 16px;'
                f'box-shadow:0 2px 12px rgba(0,0,0,.06);">{"".join(corpo)}</div>', unsafe_allow_html=True)

    # Decisão do operador: só para recomendação com fonte sobre um ativo
    if status == "COM_FONTE" and r["recommendation_type"] != "INFORMATIVA":
        atual = assistant.decisao_atual(st.session_state, r["trace_id"])
        if atual != "PENDENTE":
            st.success(f"Decisão registrada no log de auditoria: **{atual}**")
            return
        motivo = st.text_input("Justificativa (obrigatória para rejeitar ou escalar)", key=f"mot_{i}")
        c1, c2, c3 = st.columns(3)
        for col, dec, label in ((c1, "ACEITOU", "✅ Aceitar"), (c2, "REJEITOU", "❌ Rejeitar"), (c3, "ESCALOU", "⬆️ Escalar ao Gestor")):
            if col.button(label, key=f"dec_{dec}_{i}", use_container_width=True):
                try:
                    assistant.registrar_decisao(st.session_state, st.session_state.perfil,
                                                st.session_state.user_id, r["trace_id"], dec, motivo)
                    st.rerun()
                except ValueError as erro:
                    st.error(str(erro))


def render():
    perfil = st.session_state.perfil
    st.markdown('<div class="page-header"><h1>Assistente de Troubleshooting</h1>'
                '<p>Recomendações com fonte citada, filtradas pelo seu perfil e registradas em log de auditoria</p></div>',
                unsafe_allow_html=True)
    st.caption(
        f"Perfil: **{access.PERFIS[perfil]}** · fontes liberadas para o perfil: "
        f"{', '.join(c.replace('kb_', '') for c in sorted(assistant.classes_permitidas(perfil)))} · "
        "o filtro é aplicado no serviço antes da busca (Tabela 19). "
        "Sem fonte recuperada, a pergunta vai para revisão humana.")

    tags = [e["tag"] for e in st.session_state.get("equipment_list", [])]
    st.session_state.assist_tag = st.selectbox("Ativo em contexto (opcional se a TAG estiver na pergunta)",
                                               [None] + tags, format_func=lambda t: t or "— nenhum —")

    st.markdown("**Perguntas de exemplo**")
    cols = st.columns(len(EXEMPLOS))
    for col, ex in zip(cols, EXEMPLOS):
        if col.button(ex, key=f"ex_{ex}", use_container_width=True):
            _perguntar(ex)

    pergunta = st.chat_input("Pergunte sobre um alerta, procedimento ou ativo…")
    if pergunta:
        _perguntar(pergunta)

    for i, r in enumerate(st.session_state.get("chat_assistente", [])):
        _render_resposta(i, r)

    st.caption("Protótipo: base de conhecimento com resumos simulados escritos pelo grupo (não reproduzem os "
               "manuais dos fabricantes); busca lexical e geração por templates, substituíveis por embeddings e LLM.")
