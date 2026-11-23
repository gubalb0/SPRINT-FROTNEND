"""
ORQUESTRAÇÃO DO MONITORAMENTO (Sprint 4).

Na Sprint 3 o ciclo de análise vivia dentro de `pages/operations_panel.py`,
o que fazia cada página depender de o Painel ter sido aberto primeiro. Aqui
ele passa a ser um serviço sem dependência de Streamlit: recebe qualquer
"state" mutável (o `st.session_state` em produção, um `dict` nos testes).

Responsabilidades:
  - executar um ciclo do modelo analítico e propagar o estado aos ativos;
  - validar cada evento contra o contrato antes de exibir (eventos inválidos
    são descartados e registrados, sem derrubar a tela);
  - gerar um trace_id por ciclo (rastreabilidade);
  - registrar ações do operador (reconhecer alerta) e feedback sobre os
    textos gerados por NLP.
"""

from datetime import datetime
import uuid

from services import alert_engine

CHAVES_SIMULACAO = (
    "ciclo_analise", "estados_ativos", "eventos_novos", "mudancas_estado",
    "historico_eventos", "ultima_analise", "trace_id", "reconhecimentos",
    "feedback_nlp", "erros_contrato",
)


def novo_trace_id() -> str:
    return uuid.uuid4().hex[:12]


def executar_ciclo(state) -> dict:
    """Executa um ciclo de análise e atualiza o state. Retorna um resumo do ciclo."""
    ciclo = state.get("ciclo_analise", 0)
    trace_id = novo_trace_id()

    eventos_brutos, estados = alert_engine.detectar_anomalias(ciclo)

    eventos, erros = [], []
    for ev in eventos_brutos:
        problemas = alert_engine.validar_evento(ev)
        if problemas:
            erros.append({"trace_id": trace_id, "evento": ev.get("id"), "problemas": problemas})
            continue
        ev["trace_id"] = trace_id
        eventos.append(ev)

    anteriores = state.get("estados_ativos", {})
    mudancas = {
        tag: novo for tag, novo in estados.items()
        if anteriores.get(tag) and anteriores[tag] != novo
    }

    # Fonte única de verdade: o estado do modelo é propagado ao cadastro
    for eq in state.get("equipment_list", []):
        if eq["tag"] in estados:
            eq["saude"] = estados[eq["tag"]]

    state["estados_ativos"] = estados
    state["mudancas_estado"] = mudancas
    state["eventos_novos"] = eventos
    state["historico_eventos"] = state.get("historico_eventos", []) + eventos
    state["erros_contrato"] = state.get("erros_contrato", []) + erros
    state["ultima_analise"] = datetime.now()
    state["trace_id"] = trace_id

    if ciclo < alert_engine.total_ciclos() - 1:
        state["ciclo_analise"] = ciclo + 1
    else:
        state["ciclo_analise"] = ciclo

    return {"trace_id": trace_id, "eventos": len(eventos), "descartados": len(erros)}


def garantir_inicializado(state) -> None:
    """Garante que exista ao menos um ciclo executado, qualquer que seja a página aberta."""
    if "ciclo_analise" not in state:
        state["ciclo_analise"] = 0
    if "estados_ativos" not in state:
        executar_ciclo(state)


def reiniciar(state) -> None:
    for k in CHAVES_SIMULACAO:
        state.pop(k, None)


def alertas_ativos(state) -> list:
    """Evento mais recente por (tag, métrica), críticos primeiro."""
    historico = state.get("historico_eventos", [])
    vistos, ativos = set(), []
    for ev in reversed(historico):
        if ev["severidade"] not in ("critico", "atencao"):
            continue
        chave = (ev["tag"], ev["metrica"])
        if chave not in vistos:
            vistos.add(chave)
            ativos.append(ev)
    ordem = {"critico": 0, "atencao": 1}
    ativos.sort(key=lambda e: ordem.get(e["severidade"], 2))
    return ativos


# ── Ações do operador ───────────────────────────────────────────────────────
def reconhecer_alerta(state, evento_id: str, operador: str = "Operador") -> None:
    rec = state.setdefault("reconhecimentos", {})
    if evento_id not in rec:
        rec[evento_id] = {"hora": datetime.now(), "operador": operador}


def reconhecimento(state, evento_id: str):
    return state.get("reconhecimentos", {}).get(evento_id)


def pendentes(state) -> list:
    return [e for e in alertas_ativos(state) if not reconhecimento(state, e["id"])]


# ── Feedback sobre textos de IA (observabilidade) ───────────────────────────
def registrar_feedback(state, evento_id: str, util: bool) -> None:
    ev = next((e for e in state.get("historico_eventos", []) if e["id"] == evento_id), {})
    state.setdefault("feedback_nlp", {})[evento_id] = {
        "util": util,
        "hora": datetime.now(),
        "trace_id": ev.get("trace_id"),
    }


def feedback(state, evento_id: str):
    return state.get("feedback_nlp", {}).get(evento_id)
