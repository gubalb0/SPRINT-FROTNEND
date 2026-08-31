"""
Camada de INTELIGÊNCIA ANALÍTICA (simulada).

Esta camada representa o modelo de Machine Learning responsável por detectar
anomalias nos ativos. O front-end NÃO conhece a implementação interna: ele
apenas consome `detectar_anomalias()` e recebe uma lista de dicionários no
contrato definido em `CONTRATO_ALERTA`.

Para plugar um modelo real (Sprint 4+), basta substituir o corpo de
`detectar_anomalias()` por uma chamada ao modelo/API mantendo o mesmo contrato.
"""

from datetime import datetime, timedelta
import random

CONTRATO_ALERTA = {
    "id":            "str  — identificador único do evento",
    "tag":           "str  — TAG do equipamento",
    "severidade":    "str  — 'critico' | 'atencao' | 'normal'",
    "metrica":       "str  — sensor que disparou o alerta",
    "valor":         "float— valor medido",
    "limite":        "float— limite violado",
    "score_anomalia":"float— score do modelo (0.0 a 1.0)",
    "confianca":     "float— confiança da predição (0.0 a 1.0)",
    "timestamp":     "datetime",
    "modelo":        "str  — nome/versão do modelo que gerou",
}

# ── Cenário roteirizado para demonstração ───────────────────────────────────
# Cada "ciclo" de atualização avança a simulação, permitindo demonstrar a
# transição de estado Normal → Atenção → Crítico durante a gravação do vídeo.
CENARIOS = [
    # Ciclo 0 — baseline: tudo sob controle
    {
        "eventos": [],
        "estados": {"MTR-001": "normal", "MTR-002": "atencao", "MTR-003": "normal"},
    },
    # Ciclo 1 — primeiro desvio detectado no MTR-003
    {
        "eventos": [
            {
                "tag": "MTR-003",
                "severidade": "atencao",
                "metrica": "vibracao_mms",
                "valor": 3.1,
                "limite": 2.8,
                "score_anomalia": 0.62,
                "confianca": 0.88,
            },
        ],
        "estados": {"MTR-001": "normal", "MTR-002": "atencao", "MTR-003": "atencao"},
    },
    # Ciclo 2 — MTR-002 escala para crítico
    {
        "eventos": [
            {
                "tag": "MTR-002",
                "severidade": "critico",
                "metrica": "temperatura_c",
                "valor": 84.3,
                "limite": 80.0,
                "score_anomalia": 0.91,
                "confianca": 0.94,
            },
        ],
        "estados": {"MTR-001": "normal", "MTR-002": "critico", "MTR-003": "atencao"},
    },
    # Ciclo 3 — MTR-002 confirma padrão de falha (2 sensores)
    {
        "eventos": [
            {
                "tag": "MTR-002",
                "severidade": "critico",
                "metrica": "vibracao_mms",
                "valor": 5.2,
                "limite": 4.5,
                "score_anomalia": 0.95,
                "confianca": 0.96,
            },
        ],
        "estados": {"MTR-001": "normal", "MTR-002": "critico", "MTR-003": "atencao"},
    },
    # Ciclo 4 — MTR-001 apresenta desvio leve de corrente
    {
        "eventos": [
            {
                "tag": "MTR-001",
                "severidade": "atencao",
                "metrica": "corrente_a",
                "valor": 24.1,
                "limite": 23.6,
                "score_anomalia": 0.55,
                "confianca": 0.81,
            },
        ],
        "estados": {"MTR-001": "atencao", "MTR-002": "critico", "MTR-003": "atencao"},
    },
]

MODELO_VERSAO = "IsolationForest v0.3 (simulado)"

LABEL_METRICA = {
    "temperatura_c": "Temperatura",
    "vibracao_mms":  "Vibração",
    "corrente_a":    "Corrente",
    "rotacao_rpm":   "Rotação",
    "tensao_v":      "Tensão",
    "potencia_kw":   "Potência Ativa",
}

UNIDADE_METRICA = {
    "temperatura_c": "°C",
    "vibracao_mms":  "mm/s",
    "corrente_a":    "A",
    "rotacao_rpm":   "RPM",
    "tensao_v":      "V",
    "potencia_kw":   "kW",
}


def detectar_anomalias(ciclo: int):
    """
    Executa uma 'inferência' do modelo analítico.

    Args:
        ciclo: índice do ciclo de atualização (avança a cada refresh).

    Returns:
        (novos_eventos, estados_atualizados)
        novos_eventos: list[dict] no formato CONTRATO_ALERTA
        estados_atualizados: dict {tag: severidade}
    """
    idx = min(ciclo, len(CENARIOS) - 1)
    cenario = CENARIOS[idx]

    agora = datetime.now()
    eventos = []
    for i, ev in enumerate(cenario["eventos"]):
        eventos.append({
            "id": f"EVT-{agora.strftime('%H%M%S')}-{i}",
            "tag": ev["tag"],
            "severidade": ev["severidade"],
            "metrica": ev["metrica"],
            "metrica_label": LABEL_METRICA.get(ev["metrica"], ev["metrica"]),
            "unidade": UNIDADE_METRICA.get(ev["metrica"], ""),
            "valor": ev["valor"],
            "limite": ev["limite"],
            "score_anomalia": ev["score_anomalia"],
            "confianca": ev["confianca"],
            "timestamp": agora,
            "modelo": MODELO_VERSAO,
        })

    return eventos, dict(cenario["estados"])


def total_ciclos():
    return len(CENARIOS)
