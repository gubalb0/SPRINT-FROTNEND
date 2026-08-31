"""
Camada de NLP / GERAÇÃO DE LINGUAGEM NATURAL (simulada).

Responsável por transformar os eventos brutos do modelo analítico em:
  1. Resumos textuais legíveis para o operador
  2. Descrições do estado operacional do ativo
  3. Recomendações de ação para a equipe de manutenção

O front-end consome apenas as funções públicas abaixo e não conhece a
implementação. Para plugar um LLM real (Sprint 4+), basta substituir os
templates por chamadas de API mantendo a mesma assinatura e retorno.

    Exemplo de substituição futura:
        def resumir_evento(evento, equipamento):
            return llm.invoke(PROMPT_RESUMO.format(**evento))
"""

MOTOR_NLP = "Template Engine v0.2 (placeholder — substituível por LLM)"


# ── Causas prováveis por métrica ────────────────────────────────────────────
_CAUSAS = {
    "temperatura_c": [
        "sobrecarga contínua acima da potência nominal",
        "ventilação obstruída ou filtro saturado",
        "degradação do isolamento do enrolamento",
    ],
    "vibracao_mms": [
        "desgaste de rolamento",
        "desbalanceamento do eixo ou acoplamento",
        "desalinhamento entre motor e carga acionada",
    ],
    "corrente_a": [
        "aumento de carga mecânica no eixo",
        "desequilíbrio entre fases da alimentação",
        "início de curto entre espiras do enrolamento",
    ],
    "rotacao_rpm": [
        "escorregamento excessivo por sobrecarga",
        "variação na frequência de alimentação",
    ],
    "tensao_v": [
        "instabilidade na rede de alimentação",
        "queda de tensão por dimensionamento de cabo",
    ],
    "potencia_kw": [
        "operação acima do regime nominal de projeto",
    ],
}

# ── Ações recomendadas por métrica e severidade ────────────────────────────
_ACOES = {
    ("temperatura_c", "critico"): {
        "titulo": "Inspeção térmica imediata",
        "prazo": "Imediato",
        "equipe": "Manutenção Elétrica",
        "passos": [
            "Reduzir carga do motor ou programar parada controlada",
            "Realizar termografia no enrolamento e mancais",
            "Verificar obstrução do sistema de ventilação",
            "Medir resistência de isolamento (megôhmetro)",
        ],
    },
    ("temperatura_c", "atencao"): {
        "titulo": "Monitoramento térmico reforçado",
        "prazo": "24 horas",
        "equipe": "Operação",
        "passos": [
            "Aumentar frequência de leitura para intervalos de 5 min",
            "Inspecionar limpeza das aletas de refrigeração",
            "Registrar condição ambiente da área",
        ],
    },
    ("vibracao_mms", "critico"): {
        "titulo": "Análise de vibração e parada programada",
        "prazo": "Imediato",
        "equipe": "Manutenção Mecânica",
        "passos": [
            "Programar parada para inspeção de rolamentos",
            "Executar análise espectral de vibração",
            "Verificar alinhamento do acoplamento",
            "Providenciar rolamento reserva no almoxarifado",
        ],
    },
    ("vibracao_mms", "atencao"): {
        "titulo": "Acompanhamento de tendência mecânica",
        "prazo": "72 horas",
        "equipe": "Manutenção Mecânica",
        "passos": [
            "Coletar assinatura de vibração para comparação",
            "Verificar fixação da base e chumbadores",
            "Inspecionar lubrificação dos mancais",
        ],
    },
    ("corrente_a", "critico"): {
        "titulo": "Verificação elétrica urgente",
        "prazo": "Imediato",
        "equipe": "Manutenção Elétrica",
        "passos": [
            "Medir corrente nas três fases e verificar desequilíbrio",
            "Inspecionar conexões e terminais do quadro",
            "Avaliar carga mecânica acionada",
        ],
    },
    ("corrente_a", "atencao"): {
        "titulo": "Checagem de carga e alimentação",
        "prazo": "48 horas",
        "equipe": "Manutenção Elétrica",
        "passos": [
            "Registrar corrente por fase em três medições",
            "Conferir dimensionamento da proteção",
        ],
    },
}

_ACAO_PADRAO = {
    "titulo": "Verificação operacional",
    "prazo": "72 horas",
    "equipe": "Operação",
    "passos": [
        "Registrar leitura manual do sensor",
        "Comparar com histórico das últimas 24 horas",
    ],
}


def resumir_evento(evento: dict, equipamento: dict) -> str:
    """Gera o resumo textual em linguagem natural de um evento de anomalia."""
    metrica = evento["metrica"]
    label   = evento.get("metrica_label", metrica)
    unidade = evento.get("unidade", "")
    valor   = evento["valor"]
    limite  = evento["limite"]
    desvio  = ((valor - limite) / limite * 100) if limite else 0
    sev     = evento["severidade"]
    conf    = evento.get("confianca", 0) * 100
    causas  = _CAUSAS.get(metrica, ["desvio operacional não classificado"])
    nome    = equipamento.get("nome", evento["tag"])
    local   = equipamento.get("local_instalacao", "local não informado")

    if sev == "critico":
        abertura = (
            f"O modelo analítico identificou uma anomalia severa no {nome} "
            f"({evento['tag']}), instalado em {local}."
        )
        corpo = (
            f"A leitura de {label} atingiu {valor} {unidade}, "
            f"ultrapassando em {desvio:.1f}% o limite crítico de {limite} {unidade}. "
            f"O padrão observado é compatível com {causas[0]}"
        )
        if len(causas) > 1:
            corpo += f", podendo também indicar {causas[1]}"
        corpo += "."
        fecho = (
            f"Recomenda-se intervenção imediata da equipe de manutenção. "
            f"Confiança da detecção: {conf:.0f}%."
        )
    elif sev == "atencao":
        abertura = (
            f"Foi detectado um desvio de comportamento no {nome} ({evento['tag']})."
        )
        corpo = (
            f"A {label} registrou {valor} {unidade}, acima do limite de atenção "
            f"de {limite} {unidade} (desvio de {desvio:.1f}%). "
            f"A hipótese mais provável é {causas[0]}."
        )
        fecho = (
            f"O ativo permanece operacional, mas requer acompanhamento reforçado. "
            f"Confiança da detecção: {conf:.0f}%."
        )
    else:
        abertura = f"O {nome} ({evento['tag']}) opera dentro dos parâmetros esperados."
        corpo = f"A leitura de {label} está em {valor} {unidade}, dentro da faixa nominal."
        fecho = "Nenhuma ação requerida."

    return f"{abertura} {corpo} {fecho}"


def descrever_estado(equipamento: dict, severidade: str) -> str:
    """Gera a descrição textual do estado operacional atual do ativo."""
    nome = equipamento.get("nome", "Equipamento")
    tag  = equipamento.get("tag", "")
    pot  = equipamento.get("potencia_kw", "—")
    local = equipamento.get("local_instalacao", "—")

    if severidade == "critico":
        return (
            f"{nome} ({tag}) encontra-se em estado CRÍTICO. O ativo de {pot} kW "
            f"instalado em {local} apresenta desvios simultâneos que caracterizam "
            f"falha em desenvolvimento. A continuidade da operação nesta condição "
            f"eleva o risco de parada não programada."
        )
    if severidade == "atencao":
        return (
            f"{nome} ({tag}) encontra-se em estado de ATENÇÃO. O ativo continua "
            f"operando, porém apresenta tendência de desvio que deve ser acompanhada. "
            f"Não há necessidade de parada imediata."
        )
    return (
        f"{nome} ({tag}) opera em condição NORMAL. Todos os sensores registram "
        f"valores dentro da faixa nominal de projeto, sem desvios relevantes "
        f"identificados pelo modelo analítico."
    )


def recomendar_acao(evento: dict) -> dict:
    """Retorna o card de recomendação de ação para um evento."""
    chave = (evento["metrica"], evento["severidade"])
    acao = _ACOES.get(chave, _ACAO_PADRAO)
    return {
        "tag": evento["tag"],
        "severidade": evento["severidade"],
        "titulo": acao["titulo"],
        "prazo": acao["prazo"],
        "equipe": acao["equipe"],
        "passos": acao["passos"],
    }


def resumo_executivo(estados: dict, equipamentos: list) -> str:
    """Gera o resumo executivo textual de todo o parque de ativos."""
    total    = len(estados)
    criticos = [t for t, s in estados.items() if s == "critico"]
    atencao  = [t for t, s in estados.items() if s == "atencao"]
    normais  = [t for t, s in estados.items() if s == "normal"]

    partes = [f"O parque monitorado conta com {total} ativos."]

    if criticos:
        lista = ", ".join(criticos)
        partes.append(
            f"{len(criticos)} ativo(s) em estado crítico ({lista}) exigem "
            f"intervenção prioritária da equipe de manutenção."
        )
    if atencao:
        lista = ", ".join(atencao)
        partes.append(
            f"{len(atencao)} ativo(s) apresentam desvios em acompanhamento ({lista})."
        )
    if normais and not criticos and not atencao:
        partes.append("Todos os ativos operam dentro dos parâmetros nominais.")
    elif normais:
        partes.append(f"Os demais {len(normais)} ativo(s) operam normalmente.")

    if criticos:
        partes.append(
            "Prioridade operacional: tratar os ativos críticos antes do próximo turno."
        )

    return " ".join(partes)
