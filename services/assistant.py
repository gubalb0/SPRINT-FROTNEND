"""
ASSISTENTE DE TROUBLESHOOTING GOVERNADO (Sprint 4 — capítulo 6 da documentação).

Fluxo de uma pergunta:
  1. Sanitiza a pergunta (remove tokens, senhas, e-mails).
  2. Verifica pedidos explícitos de dados fora do perfil -> ACESSO_NEGADO.
  3. Monta o contexto operacional com a MESMA política das telas
     (alertas ativos, telemetria completa ou resumo, conforme Tabela 19).
  4. Recupera trechos da base de conhecimento, com filtro por access_class
     aplicado ANTES da busca e apenas versões vigentes.
  5. Aplica a regra de citação (Tabela 22): sem fonte -> revisão humana (H2).
  6. Verifica se toda citação pertence aos trechos recuperados (senão bloqueia, H5).
  7. Registra a interação no log de auditoria (Tabela 21), append-only e assinado.

Sem dependência de Streamlit: recebe qualquer "state" mutável (session_state ou dict).

Protótipo: a busca é lexical (palavras-chave com peso) e a geração usa templates,
como o nlp_service. Em produção, ambos seriam substituídos por embeddings + LLM
sem mudar o contrato de saída nem o log.
"""

from datetime import datetime
import hashlib
import hmac
import json
import os
import re
import unicodedata
import uuid

from services import access, alert_engine, contracts, monitoring
from services.knowledge_base import CHUNKS, KB_VERSION

LLM_MODEL_VERSION = "template-nlp v1.0 (simulado; substituível por LLM)"
EMBEDDING_MODEL_VERSION = "lexical-kw v1.0 (simulado; substituível por embeddings)"
LIMIAR_SIMILARIDADE = 0.75   # mesmo limiar do cadastro por visão computacional (Tabela 5)
MAX_CITACOES = 2
LOG_KEY = "audit_log_assistente"

# ── Segredos: vêm do ambiente (Vault em produção), nunca do código ──────────
def _segredo(nome):
    valor = os.environ.get(nome)
    return (valor or f"dev-only-{nome}").encode(), ("ambiente" if valor else "dev")


# ── Texto ───────────────────────────────────────────────────────────────────
STOPWORDS = {
    "a", "o", "os", "as", "um", "uma", "de", "do", "da", "dos", "das", "e", "em", "no", "na",
    "nos", "nas", "para", "por", "com", "que", "qual", "quais", "como", "se", "eu", "meu", "minha",
    "esta", "esse", "essa", "isso", "ao", "aos", "ou", "mais", "me", "mostre", "mostrar", "ver",
    "fazer", "faco", "devo", "deve", "acao", "recomendacao", "recomenda", "problema", "alerta",
    "status", "situacao", "ajuda", "agora", "hoje", "motor", "equipamento", "ativo", "sobre", "tem",
    "esta", "estao", "atual", "quero", "saber", "pode", "preciso", "o que",
}

MASCARAS = [
    (re.compile(r"(?i)bearer\s+[a-z0-9\-\._~\+/]+=*"), "Bearer [REMOVIDO]"),
    (re.compile(r"(?i)(api[_-]?key|token|senha|password|secret)\s*[:=]\s*\S+"), r"\1=[REMOVIDO]"),
    (re.compile(r"\bsk-[A-Za-z0-9]{8,}\b"), "[REMOVIDO]"),
    (re.compile(r"[\w\.-]+@[\w\.-]+\.\w+"), "[EMAIL REMOVIDO]"),
]

TAG_RE = re.compile(r"\bMTR-\d{3}\b", re.IGNORECASE)


def sanitizar(texto: str) -> str:
    for padrao, troca in MASCARAS:
        texto = padrao.sub(troca, texto)
    return texto


def _norm(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def _tokens(texto: str) -> set:
    out = set()
    for tok in re.findall(r"[a-z0-9]+", _norm(TAG_RE.sub(" ", texto))):
        if len(tok) > 4 and tok.endswith("s"):
            tok = tok[:-1]
        if tok not in STOPWORDS and len(tok) > 1:
            out.add(tok)
    return out


# Pedidos explícitos de recursos restritos (seção 6.1)
PEDIDOS_RESTRITOS = [
    ({"bruto", "adc"}, "dados_brutos", "dados brutos do ADC"),
    ({"log", "auditoria"}, "log_auditoria", "log de auditoria"),
    ({"usuario", "senha", "permissao", "credencial", "login"}, "usuarios_permissoes", "usuários, permissões e credenciais"),
    ({"card"}, "kb_model_card", "Model Card e configuração dos modelos"),
]

CTX_METRICA = {
    "temperatura_c": {"temperatura", "aquecimento"},
    "vibracao_mms": {"vibracao"},
    "corrente_a": {"corrente"},
}

SEVERIDADE_NIVEL = {
    "critico": ("Nível 3 — Crítico", "24 horas"),
    "atencao": ("Nível 1 — Atenção", "7 dias"),
}


# ── Contexto operacional (mesma política das telas) ─────────────────────────
def contexto_operacional(state, perfil, tag):
    if not tag:
        return {"alertas": [], "telemetria": None, "nivel_telemetria": None}
    alertas = [a for a in monitoring.alertas_ativos(state) if a["tag"] == tag] if access.pode(perfil, "alertas") else []
    nivel_tel = access.nivel(perfil, "telemetria_tempo_real")
    telemetria = None
    hist = (state.get("historicos") or {}).get(tag) or []
    if nivel_tel and hist:
        ult = hist[-1]
        if nivel_tel == "resumo":
            telemetria = {m: contracts.classificar(m, ult[m]) for m in ("temperatura_c", "vibracao_mms")}
        else:
            telemetria = {m: ult[m] for m in ("temperatura_c", "vibracao_mms", "corrente_a")}
    return {"alertas": alertas, "telemetria": telemetria, "nivel_telemetria": nivel_tel}


def _equipamento(state, tag):
    return next((e for e in state.get("equipment_list", []) if e["tag"] == tag), None)


# ── Recuperação com filtro por perfil ANTES da busca ────────────────────────
def classes_permitidas(perfil) -> set:
    return {k for k in access.POLITICA if k.startswith("kb_") and access.pode(perfil, k)}


def recuperar(perfil, termos_pergunta: set, termos_contexto: set):
    """
    Retorna (trechos_ordenados, filtro_aplicado). Cada trecho vem com 'similaridade'.
    Similaridade lexical: s = 2*(termos da pergunta) + 1*(termos de contexto); sim = s/(s+1).
    Se a pergunta tem termos de conteúdo, o trecho precisa casar ao menos um deles.
    """
    permitidas = classes_permitidas(perfil)
    candidatos = [c for c in CHUNKS if c["vigente"] and c["access_class"] in permitidas]
    resultado = []
    for c in candidatos:
        kw = _tokens(" ".join(c["keywords"]))   # mesma normalização da pergunta
        q = len(termos_pergunta & kw)
        k = len((termos_contexto - termos_pergunta) & kw)
        if termos_pergunta and q == 0:
            continue
        s = 2 * q + k
        if s == 0:
            continue
        resultado.append({**c, "similaridade": round(s / (s + 1), 2), "_q": q})
    # prioridade aos trechos que casam termos da própria pergunta; depois, similaridade
    resultado.sort(key=lambda c: (c["_q"], c["similaridade"]), reverse=True)
    return resultado, sorted(permitidas)


def verificar_citacoes(citacoes: list, recuperados: list) -> bool:
    """Toda citação precisa ser de um trecho efetivamente recuperado para este perfil."""
    ids = {c["chunk_id"] for c in recuperados}
    return all(c["chunk_id"] in ids for c in citacoes)


# ── Log de auditoria (Tabela 21) ────────────────────────────────────────────
def pseudonimo(user_id: str) -> str:
    salt, _ = _segredo("FORZY_PSEUDO_SALT")
    return hmac.new(salt, user_id.encode(), hashlib.sha256).hexdigest()[:16]


def _assinar(registro: dict) -> str:
    chave, _ = _segredo("FORZY_AUDIT_KEY")
    corpo = json.dumps({k: v for k, v in registro.items() if k != "digital_signature"},
                       sort_keys=True, default=str, ensure_ascii=False)
    return hmac.new(chave, corpo.encode(), hashlib.sha256).hexdigest()


def verificar_assinatura(registro: dict) -> bool:
    return hmac.compare_digest(registro.get("digital_signature", ""), _assinar(registro))


def _anexar_log(state, registro: dict) -> dict:
    log = state.setdefault(LOG_KEY, [])
    registro["previous_event_id"] = log[-1]["event_id"] if log else None
    registro["digital_signature"] = _assinar(registro)
    log.append(registro)          # append-only: não há função de edição ou exclusão
    return registro


def log_auditoria(state, perfil) -> list:
    """Leitura do log, com autorização no serviço (Tabela 2: log de auditoria)."""
    access.exigir(perfil, "log_auditoria")
    return list(state.get(LOG_KEY, []))


# ── Pergunta ────────────────────────────────────────────────────────────────
def perguntar(state, perfil: str, user_id: str, pergunta: str, tag: str | None = None) -> dict:
    access.exigir(perfil, "assistente")
    agora = datetime.now()
    trace_id = uuid.uuid4().hex[:12]
    pergunta_limpa = sanitizar(pergunta)

    achado = TAG_RE.search(pergunta)
    tag = (achado.group(0).upper() if achado else tag) or None
    termos = _tokens(pergunta_limpa)

    resp = {
        "trace_id": trace_id, "tag": tag, "perfil": perfil,
        "citation_status": None, "recommendation_type": "INFORMATIVA",
        "texto": "", "citacoes": [], "dado_operacional": [], "handoff_level": None,
        "nivel": None, "prazo": None, "citacao_invalida": False,
    }

    # 2) pedido explícito de recurso restrito
    negado = None
    for gatilhos, recurso, nome in PEDIDOS_RESTRITOS:
        if termos & gatilhos and (recurso in access.NUNCA_RECUPERAVEL or not access.pode(perfil, recurso)):
            negado = (recurso, nome)
            break
    if not negado and "valor" in termos and access.nivel(perfil, "telemetria_tempo_real") in (None, "resumo"):
        negado = ("telemetria_tempo_real", "valores absolutos de telemetria")

    ctx = {"alertas": [], "telemetria": None, "nivel_telemetria": None}
    recuperados, filtro = [], sorted(classes_permitidas(perfil))

    if negado:
        recurso, nome = negado
        quem = [] if recurso in access.NUNCA_RECUPERAVEL else access.perfis_com_acesso(recurso)
        if recurso == "telemetria_tempo_real":
            quem = [access.PERFIS[p] for p in access.PERFIS if access.nivel(p, recurso) == "total"]
        resp["citation_status"] = "ACESSO_NEGADO"
        resp["texto"] = (f"O perfil {access.PERFIS[perfil]} não tem acesso a: {nome}. "
                         + (f"Esse conteúdo é restrito a: {', '.join(quem)}." if quem
                            else "Esse conteúdo nunca é recuperado pelo assistente."))
        if recurso == "dados_brutos" and access.nivel(perfil, "telemetria_tempo_real") == "resumo":
            resp["texto"] += " Você pode consultar o resumo de temperatura e vibração na tela de Telemetria."
    else:
        # 3) contexto operacional
        ctx = contexto_operacional(state, perfil, tag)
        eq = _equipamento(state, tag) if tag else None
        termos_ctx = set()
        for a in ctx["alertas"]:
            termos_ctx |= CTX_METRICA.get(a["metrica"], set())
        if eq:
            termos_ctx |= _tokens(f"{eq.get('fabricante', '')} {eq.get('nome', '')}")

        # 4) recuperação filtrada
        recuperados, filtro = recuperar(perfil, termos, termos_ctx)
        fontes = [c for c in recuperados if c["similaridade"] >= LIMIAR_SIMILARIDADE][:MAX_CITACOES]

        for a in ctx["alertas"]:
            ref = f" ({contracts.referencia(a['metrica'])})" if contracts.tem_contrato(a["metrica"]) else ""
            resp["dado_operacional"].append(
                f"{a['metrica_label']} {a['valor']} {a['unidade']}, limite {a['limite']} {a['unidade']}{ref}; "
                f"score {a['score_anomalia']:.2f}, confiança {a['confianca']:.0%}, modelo {a['modelo']}")
        if ctx["telemetria"] and ctx["nivel_telemetria"] == "resumo":
            resp["dado_operacional"].append("Telemetria (resumo do perfil): " + ", ".join(
                f"{m.split('_')[0]} na faixa {f}" for m, f in ctx["telemetria"].items()))

        pior = next((a for a in ctx["alertas"]), None)
        if pior:
            resp["nivel"], resp["prazo"] = SEVERIDADE_NIVEL.get(pior["severidade"], (None, None))

        # 5) regra de citação (Tabela 22)
        if fontes:
            resp["citation_status"] = "COM_FONTE"
            resp["citacoes"] = fontes
            principal = fontes[0]
            if pior:
                resp["recommendation_type"] = principal["recomendacao"]
                resp["texto"] = _texto_recomendacao(principal, tag, resp["nivel"], resp["prazo"])
            else:
                resp["texto"] = f"Informação do documento citado: {principal['texto']}"
        else:
            resp["citation_status"] = "SEM_FONTE_REVISAO"
            resp["handoff_level"] = "H2"
            if ctx["alertas"]:
                resp["texto"] = ("Encontrei o alerta e os dados do ativo, mas nenhum procedimento documentado "
                                 "autorizado para o seu perfil responde a esta pergunta. A pergunta foi "
                                 "encaminhada para revisão humana (handoff H2, prazo de 72 horas).")
            elif tag:
                resp["texto"] = (f"Não há alerta ativo para o {tag} no momento e não encontrei procedimento "
                                 "documentado autorizado para o seu perfil que responda a esta pergunta. "
                                 "Nenhuma recomendação foi gerada; a pergunta foi encaminhada para revisão humana (handoff H2).")
            else:
                resp["texto"] = ("Não encontrei fonte autorizada para o seu perfil que responda a esta pergunta. "
                                 "Nenhuma recomendação foi gerada; a pergunta foi encaminhada para revisão "
                                 "humana (handoff H2).")

        # 6) verificador de citações
        if resp["citacoes"] and not verificar_citacoes(resp["citacoes"], recuperados):
            resp.update(citation_status="SEM_FONTE_REVISAO", citacao_invalida=True, handoff_level="H5",
                        texto="Resposta bloqueada: a citação não corresponde a um trecho recuperado.", citacoes=[])

    # 7) log de auditoria
    _, origem_chave = _segredo("FORZY_AUDIT_KEY")
    registro = {
        "event_id": uuid.uuid4().hex[:12],
        "event_type": "INTERACAO",
        "trace_id": trace_id,
        "session_id": state.setdefault("session_id", uuid.uuid4().hex[:12]),
        "monitoring_trace_id": state.get("trace_id"),
        "request_timestamp": agora.isoformat(timespec="seconds"),
        "response_timestamp": datetime.now().isoformat(timespec="seconds"),
        "user_pseudo_id": pseudonimo(user_id),
        "user_role": perfil,
        "asset_tag": tag,
        "query_text_sanitized": pergunta_limpa,
        "access_filter_applied": filtro,
        "retrieved_sources": [
            {"doc_id": c["doc_id"], "doc_version": c["doc_version"], "secao": c["secao"],
             "chunk_id": c["chunk_id"], "similaridade": c["similaridade"]} for c in recuperados[:5]],
        "operational_refs": {
            "alert_ids": [a["id"] for a in ctx["alertas"]],
            "metric_contracts": sorted({contracts.referencia(a["metrica"]) for a in ctx["alertas"]
                                        if contracts.tem_contrato(a["metrica"])}),
        },
        "llm_model_version": LLM_MODEL_VERSION,
        "knowledge_base_version": KB_VERSION,
        "embedding_model_version": EMBEDDING_MODEL_VERSION,
        "prediction_model_version": alert_engine.MODELO_VERSAO if ctx["alertas"] else None,
        "citation_status": resp["citation_status"],
        "citacao_invalida": resp["citacao_invalida"],
        "recommendation_type": resp["recommendation_type"],
        "operator_decision": "PENDENTE",
        "decision_timestamp": None,
        "decision_reason": None,
        "handoff_level": resp["handoff_level"],
        "signing_key_source": origem_chave,
    }
    _anexar_log(state, registro)
    return resp


def _texto_recomendacao(chunk, tag, nivel, prazo):
    alvo = f"do {tag}" if tag else ""
    base = {
        "TROCA_ROLAMENTO": f"Programar a substituição do rolamento {alvo} em até {prazo} ({nivel}).",
        "LUBRIFICACAO": f"Verificar e corrigir a lubrificação dos mancais {alvo} em até {prazo} ({nivel}).",
        "INSPECAO": f"Inspecionar o ativo {tag} conforme o procedimento citado em até {prazo} ({nivel}).",
        "PARADA_PROGRAMADA": f"Programar a parada {alvo} em até {prazo} ({nivel}), seguindo o procedimento citado.",
        "AJUSTE_THRESHOLD": ("O assistente não altera limiares. Para mudar a faixa, abra solicitação de mudança "
                             "do Metric Contract (mudança MAJOR, com aprovação e Banner de Ruptura)."),
    }.get(chunk["recomendacao"], f"Consultar o procedimento citado para o ativo {tag}.")
    return f"{base} Procedimento de referência: {chunk['texto']}"


# ── Decisão do operador (fecha o ciclo de responsabilidade) ─────────────────
DECISOES = ("ACEITOU", "REJEITOU", "ESCALOU")


def registrar_decisao(state, perfil, user_id, trace_id, decisao, motivo=""):
    if decisao not in DECISOES:
        raise ValueError(f"decisão inválida: {decisao}")
    if decisao in ("REJEITOU", "ESCALOU") and not motivo.strip():
        raise ValueError("Justificativa obrigatória para rejeitar ou escalar.")
    original = next((r for r in state.get(LOG_KEY, []) if r["trace_id"] == trace_id and r["event_type"] == "INTERACAO"), None)
    if original is None:
        raise KeyError(trace_id)
    handoff = None
    if decisao == "ESCALOU":
        handoff = "H3" if original.get("recommendation_type") not in ("INFORMATIVA", None) else "H2"
    registro = {
        "event_id": uuid.uuid4().hex[:12],
        "event_type": "DECISAO",
        "trace_id": trace_id,
        "session_id": state.get("session_id"),
        "user_pseudo_id": pseudonimo(user_id),
        "user_role": perfil,
        "operator_decision": decisao,
        "decision_timestamp": datetime.now().isoformat(timespec="seconds"),
        "decision_reason": sanitizar(motivo) or None,
        "handoff_level": handoff,
    }
    return _anexar_log(state, registro)


def registrar_ciencia_banner(state, perfil, user_id, versao):
    """Confirmação de leitura do Banner de Ruptura (seção 7.7), registrada no log."""
    return _anexar_log(state, {
        "event_id": uuid.uuid4().hex[:12], "event_type": "CIENCIA_BANNER", "trace_id": uuid.uuid4().hex[:12],
        "session_id": state.setdefault("session_id", uuid.uuid4().hex[:12]),
        "user_pseudo_id": pseudonimo(user_id), "user_role": perfil,
        "decision_timestamp": datetime.now().isoformat(timespec="seconds"),
        "detalhe": f"Ciência do Banner de Ruptura da versão {versao}",
    })


def decisao_atual(state, trace_id) -> str:
    for r in reversed(state.get(LOG_KEY, [])):
        if r["trace_id"] == trace_id and r["event_type"] == "DECISAO":
            return r["operator_decision"]
    return "PENDENTE"
