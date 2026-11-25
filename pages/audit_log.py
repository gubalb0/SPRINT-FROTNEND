"""Log de auditoria do assistente (Tabela 21). Leitura autorizada no serviço."""

import json

import pandas as pd
import streamlit as st

from services import access, assistant


def render():
    perfil = st.session_state.perfil
    registros = assistant.log_auditoria(st.session_state, perfil)   # lança AcessoNegado se não puder

    st.markdown('<div class="page-header"><h1>Log de Auditoria do Assistente</h1>'
                '<p>Quem perguntou, o que foi recuperado, com quais versões e o que o operador decidiu</p></div>',
                unsafe_allow_html=True)
    st.caption("Append-only, assinado com HMAC-SHA256 e com usuário pseudonimizado. "
               "Sem tokens, senhas ou e-mails (mascarados antes da escrita).")

    if not registros:
        st.info("Nenhuma interação registrada ainda. Use o Assistente para gerar registros.")
        return

    if any(r.get("signing_key_source") == "dev" for r in registros):
        st.warning("Assinatura com chave de desenvolvimento. Em produção, defina FORZY_AUDIT_KEY e "
                   "FORZY_PSEUDO_SALT pelo cofre de segredos (Vault) ou variáveis de ambiente seguras.")

    linhas = [{
        "assinatura": "✔" if assistant.verificar_assinatura(r) else "✘ ALTERADO",
        "tipo": r["event_type"],
        "trace_id": r["trace_id"],
        "hora": r.get("request_timestamp") or r.get("decision_timestamp"),
        "perfil": r["user_role"],
        "usuário (pseudônimo)": r["user_pseudo_id"],
        "ativo": r.get("asset_tag"),
        "citação": r.get("citation_status"),
        "recomendação": r.get("recommendation_type"),
        "decisão": (assistant.decisao_atual(st.session_state, r["trace_id"]) + " (vigente)")
                   if r["event_type"] == "INTERACAO" else r.get("operator_decision"),
        "handoff": r.get("handoff_level"),
        "docs recuperados": ", ".join(f'{s["doc_id"]} v{s["doc_version"]}' for s in r.get("retrieved_sources", [])),
    } for r in registros]
    st.dataframe(pd.DataFrame(linhas), use_container_width=True, hide_index=True)

    sel = st.selectbox("Detalhar registro", range(len(registros)),
                       format_func=lambda i: f'{registros[i]["event_type"]} · {registros[i]["trace_id"]}')
    st.json(registros[sel])

    if access.pode(perfil, "log_auditoria"):
        st.download_button("⬇️ Exportar log assinado (JSON)",
                           json.dumps(registros, ensure_ascii=False, indent=1, default=str),
                           file_name="forzy_log_assistente.json", mime="application/json")
